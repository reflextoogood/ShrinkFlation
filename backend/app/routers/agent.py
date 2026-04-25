"""
Agent router — POST /api/v1/agent/investigate
Streams the ShrinkFlation Detective agent response.
"""
from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])


class InvestigateRequest(BaseModel):
    query: str


class InvestigateResponse(BaseModel):
    verdict: str
    query: str


@router.post("/investigate", response_model=InvestigateResponse)
async def investigate(request: InvestigateRequest):
    """
    Run the ShrinkFlation Detective agent on a product query.
    The agent autonomously searches, calculates, and produces a verdict.
    """
    if not os.environ.get("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY not configured. Set it as an environment variable.",
        )

    if not request.query.strip():
        raise HTTPException(status_code=422, detail="Query cannot be empty.")

    try:
        from app.agent.graph import run_agent
        verdict = await run_agent(request.query)
        return InvestigateResponse(verdict=verdict, query=request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.get("/health")
def agent_health():
    has_key = bool(os.environ.get("OPENAI_API_KEY"))
    return {
        "status": "ready" if has_key else "missing_api_key",
        "model": "gpt-4o",
        "tools": [
            "search_product_in_db",
            "get_quantity_history",
            "get_price_history",
            "calculate_shrinkflation_metrics",
            "search_open_food_facts",
            "get_brand_severity",
        ],
    }
