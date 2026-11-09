"""
Pydantic schemas for the Plan B endpoint.
"""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class PlanBRequest(BaseModel):
    plan_text:       str = Field(min_length=1, max_length=500)
    confirmed_lever: Literal["change_date", "change_amount", "skip_one", "none"] | None = None


class PlanBLLMResponse(BaseModel):
    card_text:  str = Field(max_length=300)
    lever:      Literal["change_date", "change_amount", "skip_one", "none"]
    faithful:   bool
    issues:     list[str]
    confidence: float = Field(ge=0.0, le=1.0)


class QualityResult(BaseModel):
    checked:  bool
    failures: list[str]


class PlanBResponse(BaseModel):
    card_text:    str | None = None
    lever:        str | None = None
    faithful:     bool | None = None
    issues:       list[str] = []
    confidence:   float | None = None
    quality:      QualityResult | None = None
    fallback:     bool = False
    issue:        Literal["unsupported_feature", "cancel_intent"] | None = None
    rewrite_offer: str | None = None

