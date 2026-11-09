"""
Lever Coach router — POST /api/lever-coach
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from schemas.lever_coach_schema import (
    LeverCoachRequest,
    LeverCoachLLMResponse,
    LeverCoachResponse,
    QualityResult,
)
from services.masking_service import mask_digits
from services.llm_service import call_llm
from services.quality_gate import run_all_checks
from config import settings

router = APIRouter()

# Load KB and prompt once at startup
_KB_PATH = Path(__file__).parent.parent / "data" / "knowledge_base.json"
_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "lever_coach_prompt.txt"

KB_JSON = _KB_PATH.read_text(encoding="utf-8") if _KB_PATH.exists() else "{}"
PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8") if _PROMPT_PATH.exists() else ""


def _compute_edit_window(sip_day: int) -> str:
    """Compute 2-working-days-before date for the given SIP day."""
    today = date.today()
    # Build SIP date for this month or next
    try:
        sip_date = today.replace(day=sip_day)
    except ValueError:
        sip_date = (today.replace(day=1) + timedelta(days=32)).replace(day=sip_day)
    if sip_date <= today:
        # Move to next month
        m = today.month % 12 + 1
        y = today.year + (1 if m == 1 else 0)
        sip_date = date(y, m, sip_day)

    # Subtract 2 working days
    remaining = 2
    deadline = sip_date
    while remaining > 0:
        deadline -= timedelta(days=1)
        if deadline.weekday() < 5:  # Mon-Fri
            remaining -= 1

    return deadline.isoformat()


@router.post("/lever-coach", response_model=LeverCoachResponse)
async def lever_coach(req: LeverCoachRequest):
    # Double-pass digit masking (client already masked; this is the safety net)
    masked_text, _ = mask_digits(req.text)

    # Build prompt
    system_prompt = PROMPT_TEMPLATE.format(
        knowledge_base_json=KB_JSON,
        skip_rules_verified=str(settings.skip_rules_verified).lower(),
        user_input=masked_text,
    )

    # Call LLM
    try:
        raw = call_llm(system_prompt, masked_text)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    # Validate with Pydantic
    try:
        validated = LeverCoachLLMResponse.model_validate(raw)
    except ValidationError as exc:
        # Schema failed → fallback
        return LeverCoachResponse(
            levers=[],
            situation_type="unclear",
            confidence=0.0,
            evidence_quote="",
            explanation="",
            fact_ids=[],
            quality=QualityResult(checked=False, failures=["schema_validation_failed"]),
            fallback=True,
        )

    response_dict = validated.model_dump()

    # Run Quality Gate
    quality = run_all_checks(response_dict, masked_text)

    # Edit-window date (plain code, not LLM)
    edit_window_date = None
    if req.sip_date:
        try:
            edit_window_date = _compute_edit_window(req.sip_date)
        except Exception:
            pass

    return LeverCoachResponse(
        levers=[l.value for l in validated.levers],
        situation_type=validated.situation_type.value,
        confidence=validated.confidence,
        evidence_quote=validated.evidence_quote,
        explanation=validated.explanation,
        fact_ids=validated.fact_ids,
        quality=QualityResult(**quality),
        edit_window_date=edit_window_date,
        fallback=not quality["checked"],
    )

