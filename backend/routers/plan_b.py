"""
Plan B router — POST /api/plan-b
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from schemas.plan_b_schema import (
    PlanBRequest,
    PlanBLLMResponse,
    PlanBResponse,
    QualityResult,
)
from services.llm_service import call_llm
from services.quality_gate import run_all_checks

router = APIRouter()

_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "plan_b_prompt.txt"
PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8") if _PROMPT_PATH.exists() else ""


@router.post("/plan-b", response_model=PlanBResponse)
async def plan_b(req: PlanBRequest):
    system_prompt = PROMPT_TEMPLATE.format(
        plan_text=req.plan_text,
        confirmed_lever=req.confirmed_lever or "none provided",
    )

    try:
        raw = call_llm(system_prompt, req.plan_text)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    try:
        validated = PlanBLLMResponse.model_validate(raw)
    except ValidationError:
        return PlanBResponse(
            fallback=True,
            quality=QualityResult(checked=False, failures=["schema_validation_failed"]),
        )

    # Handle special issues
    issues = validated.issues or []

    if "cancel_intent" in issues:
        return PlanBResponse(issue="cancel_intent")

    if "unsupported_feature" in issues and not req.confirmed_lever:
        return PlanBResponse(
            issue="unsupported_feature",
            rewrite_offer="skip_one",
        )

    response_dict = validated.model_dump()
    quality = run_all_checks(response_dict, req.plan_text)

    if not quality["checked"]:
        return PlanBResponse(
            fallback=True,
            quality=QualityResult(**quality),
        )

    return PlanBResponse(
        card_text=validated.card_text,
        lever=validated.lever,
        faithful=validated.faithful,
        issues=issues,
        confidence=validated.confidence,
        quality=QualityResult(**quality),
    )

