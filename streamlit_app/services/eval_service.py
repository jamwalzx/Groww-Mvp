"""
Eval service — runs the golden_set through the pipeline and computes metrics.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from services.masking_service import mask_digits
from services.llm_service import call_llm
from services.quality_gate import run_all_checks, BANNED_WORDS
from config import settings

_KB_PATH = Path(__file__).parent.parent / "data" / "knowledge_base.json"
_LC_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "lever_coach_prompt.txt"
_PB_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "plan_b_prompt.txt"

KB_JSON = _KB_PATH.read_text(encoding="utf-8") if _KB_PATH.exists() else "{}"
LC_PROMPT = _LC_PROMPT_PATH.read_text(encoding="utf-8") if _LC_PROMPT_PATH.exists() else ""
PB_PROMPT = _PB_PROMPT_PATH.read_text(encoding="utf-8") if _PB_PROMPT_PATH.exists() else ""

FAILURE_CATEGORIES = ["Hinglish", "Multi-lever", "Vague input", "Advice drift", "Other"]


def _categorise(row: dict) -> str:
    notes = (row.get("notes") or "").lower()
    text = (row.get("input_text") or "").lower()
    if any(w in text for w in ["tarikh", "kat", "aati", "mahina", "paisa"]):
        return "Hinglish"
    if "," in (row.get("expected_levers") or ""):
        return "Multi-lever"
    if "vague" in notes or "unclear" in notes:
        return "Vague input"
    if "advice" in notes or row.get("expected_situation_type") == "advice_request":
        return "Advice drift"
    return "Other"


async def _run_one_lever_coach(row: dict) -> dict:
    text = row["input_text"]
    masked, _ = mask_digits(text)
    prompt = LC_PROMPT.format(
        knowledge_base_json=KB_JSON,
        skip_rules_verified=str(settings.skip_rules_verified).lower(),
        user_input=masked,
    )
    try:
        raw = call_llm(prompt, masked)
    except Exception:
        return {"error": True, "row": row}

    quality = run_all_checks(raw, masked)
    return {"raw": raw, "quality": quality, "row": row}


async def _run_one_plan_b(row: dict) -> dict:
    text = row["input_text"]
    prompt = PB_PROMPT.format(
        plan_text=text,
        confirmed_lever="none provided",
    )
    try:
        raw = call_llm(prompt, text)
    except Exception:
        return {"error": True, "row": row}

    quality = run_all_checks(raw, text)
    return {"raw": raw, "quality": quality, "row": row}


async def run_eval_set(
    rows: list[dict],
    model: str,
    prompt_version: str,
    cost_cap_usd: float,
) -> dict:
    lever_exact_hits = 0
    lever_partial_hits = 0
    situation_hits = 0
    correct_refusals = 0
    false_refusals = 0
    refusal_total = 0
    should_refuse_total = 0
    banned_violations = 0
    ungrounded = 0
    card_faithful = 0
    plan_b_total = 0
    fallbacks = 0
    failures = []

    tasks = []
    for row in rows:
        section = row.get("section", "lever_coach")
        if section == "lever_coach":
            tasks.append(_run_one_lever_coach(row))
        else:
            tasks.append(_run_one_plan_b(row))

    results = await asyncio.gather(*tasks)

    for res in results:
        row = res["row"]
        section = row.get("section", "lever_coach")
        should_refuse = row.get("should_refuse", "false").lower() == "true"
        if should_refuse:
            should_refuse_total += 1

        if res.get("error"):
            fallbacks += 1
            failures.append({
                "id": row["id"],
                "category": _categorise(row),
                "input_text": row["input_text"],
                "expected_levers": row.get("expected_levers", "").split(","),
                "actual_levers": [],
                "notes": "LLM call failed",
            })
            continue

        raw = res.get("raw", {})
        quality = res.get("quality", {})

        if not quality.get("checked"):
            fallbacks += 1

        # Check banned words
        combined = " ".join(str(v) for k, v in raw.items() if k in ("explanation", "card_text")).lower()
        for w in BANNED_WORDS:
            if w in combined:
                banned_violations += 1
                break

        # Ungrounded facts
        fact_ids = raw.get("fact_ids", [])
        from services.quality_gate import VALID_FACT_IDS
        if set(fact_ids) - VALID_FACT_IDS:
            ungrounded += 1

        if section == "lever_coach":
            # Lever accuracy
            expected = {l.strip() for l in row.get("expected_levers", "").split(",") if l.strip()}
            actual = set(raw.get("levers", []))
            if expected == actual:
                lever_exact_hits += 1
            if expected & actual:
                lever_partial_hits += 1

            # Situation type
            if raw.get("situation_type") == row.get("expected_situation_type"):
                situation_hits += 1

            # Refusals
            situation = raw.get("situation_type", "")
            is_refused = situation in ("advice_request", "out_of_scope")
            if should_refuse:
                if is_refused:
                    correct_refusals += 1
                else:
                    false_refusals += 1
                    failures.append({
                        "id": row["id"],
                        "category": _categorise(row),
                        "input_text": row["input_text"],
                        "expected_levers": list(expected),
                        "actual_levers": list(actual),
                        "notes": "Should have refused but didn't",
                    })
            elif is_refused:
                false_refusals += 1

            # Track non-matching levers as failures
            if expected and expected != actual and not should_refuse:
                failures.append({
                    "id": row["id"],
                    "category": _categorise(row),
                    "input_text": row["input_text"],
                    "expected_levers": list(expected),
                    "actual_levers": list(actual),
                    "notes": row.get("notes", ""),
                })

        else:  # plan_b
            plan_b_total += 1
            if raw.get("faithful"):
                card_faithful += 1

    total = len(rows)
    lc_total = sum(1 for r in rows if r.get("section", "lever_coach") == "lever_coach")

    return {
        "total_rows": total,
        "lever_accuracy_exact": lever_exact_hits / lc_total if lc_total else 0,
        "lever_accuracy_partial": lever_partial_hits / lc_total if lc_total else 0,
        "situation_type_accuracy": situation_hits / lc_total if lc_total else 0,
        "correct_refusal_rate": correct_refusals / should_refuse_total if should_refuse_total else 1.0,
        "false_refusal_rate": false_refusals / total if total else 0,
        "banned_word_violations": banned_violations,
        "ungrounded_fact_rate": ungrounded / total if total else 0,
        "card_faithfulness_rate": card_faithful / plan_b_total if plan_b_total else 1.0,
        "fallback_rate": fallbacks / total if total else 0,
        "estimated_cost_usd": round(total * 0.0002, 4),  # rough estimate
        "failures": failures,
    }

