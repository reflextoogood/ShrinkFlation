"""
Calculator router — POST /api/v1/calculator and GET /api/v1/calculator/export
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import GroceryListRequest, GroceryListResponse
from app.services.calculator_service import calculate_grocery_list, export_csv, export_pdf

router = APIRouter(prefix="/api/v1/calculator", tags=["calculator"])


@router.post("", response_model=GroceryListResponse)
def run_calculator(request: GroceryListRequest, db: Session = Depends(get_db)):
    try:
        return calculate_grocery_list(request, db)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/export")
def export_results(
    format: str = Query(..., pattern="^(csv|pdf)$"),
    db: Session = Depends(get_db),
):
    """
    Export the last calculated grocery list.
    In a real app this would use a session/cache; here we return an empty list
    as a placeholder — the frontend should POST first then call export.
    """
    from app.schemas.api import GroceryListResponse
    empty = GroceryListResponse(items=[], total_annual_hidden_cost=0.0)

    if format == "csv":
        content = export_csv(empty)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=grocery_analysis.csv"},
        )
    else:
        content = export_pdf(empty)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=grocery_analysis.pdf"},
        )
