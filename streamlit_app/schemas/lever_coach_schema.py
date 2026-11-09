"""
Pydantic schemas for the Lever Coach endpoint.
"""
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field, field_validator


VALID_FACT_IDS = {"K1", "K2", "K3", "K3b", "K4", "K5", "K6"}


class LeverEnum(str, Enum):
    change_date     = "change_date"
    change_amount   = "change_amount"
    skip_one        = "skip_one"
    none_applicable = "none_applicable"


class SituationType(str, Enum):
    timing_gap        = "timing_gap"
    recurring_squeeze = "recurring_squeeze"
    one_off_month     = "one_off_month"
    unclear           = "unclear"
    advice_request    = "advice_request"
    out_of_scope      = "out_of_scope"


class LeverCoachRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    sip_date: int | None = Field(default=None, ge=1, le=28)


class LeverCoachLLMResponse(BaseModel):
    levers:         list[LeverEnum]
    situation_type: SituationType
    confidence:     float = Field(ge=0.0, le=1.0)
    evidence_quote: str
    explanation:    str = Field(max_length=600)
    fact_ids:       list[str]

    @field_validator("fact_ids")
    @classmethod
    def validate_fact_ids(cls, v: list[str]) -> list[str]:
        invalid = set(v) - VALID_FACT_IDS
        if invalid:
            raise ValueError(f"Unknown fact ids: {sorted(invalid)}")
        return v


class QualityResult(BaseModel):
    checked:  bool
    failures: list[str]


class LeverCoachResponse(BaseModel):
    levers:          list[str]
    situation_type:  str
    confidence:      float
    evidence_quote:  str
    explanation:     str
    fact_ids:        list[str]
    quality:         QualityResult
    edit_window_date: str | None = None
    fallback:        bool = False

