"""
Eval router — POST /api/eval/run
"""
from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.eval_service import run_eval_set
from config import settings

router = APIRouter()

_CSV_PATH = Path(__file__).parent.parent / "data" / "golden_set.csv"


class EvalRunRequest(BaseModel):
    model: str = "gpt-4o-mini"
    prompt_version: str = "v1.0"
    cost_cap_usd: float = 1.00


@router.post("/eval/run")
async def run_eval(req: EvalRunRequest):
    if not _CSV_PATH.exists():
        raise HTTPException(status_code=404, detail="golden_set.csv not found")

    rows = []
    with _CSV_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise HTTPException(status_code=400, detail="golden_set.csv is empty")

    result = await run_eval_set(
        rows=rows,
        model=req.model,
        prompt_version=req.prompt_version,
        cost_cap_usd=req.cost_cap_usd,
    )

    return {
        "run_id": datetime.now(timezone.utc).isoformat(),
        "model": req.model,
        "prompt_version": req.prompt_version,
        **result,
    }


@router.get("/eval/csv")
async def get_csv():
    """Return the golden_set.csv contents as JSON rows."""
    if not _CSV_PATH.exists():
        raise HTTPException(status_code=404, detail="golden_set.csv not found")
    rows = []
    with _CSV_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return {"rows": rows, "count": len(rows)}

