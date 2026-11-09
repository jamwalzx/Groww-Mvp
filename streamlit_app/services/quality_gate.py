"""
Quality Gate — 7 ordered checks that every LLM response must pass.
Returns (passed: bool, failures: list[str]).
"""
from __future__ import annotations

import re
from config import settings

VALID_FACT_IDS = {"K1", "K2", "K3", "K3b", "K4", "K5", "K6"}

BANNED_WORDS = [
    "hurry", "act now", "last chance", "don't miss", "dont miss",
    "limited time", "you will lose", "before it's too late",
    "before its too late", "deadline", "countdown",
]

# Simple fund/stock pattern — common Indian MF/stock identifiers
FUND_PATTERN = re.compile(
    r"\b(axis|hdfc|sbi|icici|aditya birla|mirae|nippon|kotak|dsp|franklin|"
    r"nifty|sensex|bse|nse|smallcap|midcap|largecap|flexi.?cap|"
    r"reliance|infosys|tcs|wipro|hdfc bank)\b",
    re.IGNORECASE,
)


def run_all_checks(
    response: dict,
    masked_input: str,
    *,
    confidence_threshold: float = 0.7,
) -> dict:
    failures: list[str] = []

    # 1. Confidence
    conf = response.get("confidence", 0)
    if not isinstance(conf, (int, float)) or conf < confidence_threshold:
        failures.append("confidence_below_threshold")

    # 2. All fact_ids in KB
    fact_ids = response.get("fact_ids", [])
    unknown = set(fact_ids) - VALID_FACT_IDS
    if unknown:
        failures.append(f"unknown_fact_ids:{','.join(sorted(unknown))}")

    # 3. Zero banned words in output text fields
    combined_output = " ".join(
        str(v) for k, v in response.items()
        if k in ("explanation", "card_text", "explanation")
    ).lower()
    for w in BANNED_WORDS:
        if w in combined_output:
            failures.append(f"banned_word:'{w}'")
            break

    # 4. No fund/stock name
    if FUND_PATTERN.search(combined_output):
        failures.append("fund_or_stock_name_detected")

    # 5. Schema already validated by Pydantic (router catches ValidationError)
    # (marked as passed if we got here)

    # 6. evidence_quote is exact substring of masked input
    eq = response.get("evidence_quote", "")
    if eq and eq not in masked_input:
        failures.append("evidence_quote_not_in_input")

    # 7. K3b respected
    if not settings.skip_rules_verified:
        # K3b must not be in fact_ids while flag is false
        if "K3b" in fact_ids:
            explanation = response.get("explanation", "")
            # Allow K3b only if explanation defers to confirmation screen
            if "confirmation screen" not in explanation.lower():
                failures.append("k3b_timing_stated_while_flag_false")

    passed = len(failures) == 0
    return {"checked": passed, "failures": failures}

