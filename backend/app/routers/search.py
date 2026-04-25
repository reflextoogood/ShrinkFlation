"""
Search router — GET /api/v1/search
"""
from __future__ import annotations

import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import SearchResponse
from app.services.search_service import search_by_upc_service, search_products

router = APIRouter(prefix="/api/v1/search", tags=["search"])

UPC_PATTERN = re.compile(r"^\d{8,14}$")


@router.get("", response_model=SearchResponse)
def search(
    q: Optional[str] = Query(None, min_length=1, max_length=200),
    upc: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    if upc is not None:
        if not UPC_PATTERN.match(upc):
            raise HTTPException(
                status_code=422,
                detail="UPC must be 8–14 numeric digits only.",
            )
        result, off_unavailable = search_by_upc_service(upc, db)
        results = [result] if result else []
        return SearchResponse(
            results=results,
            off_unavailable=off_unavailable,
            total=len(results),
        )

    if q is not None:
        if len(q) < 1 or len(q) > 200:
            raise HTTPException(
                status_code=422,
                detail="Query must be between 1 and 200 characters.",
            )
        return search_products(q, db)

    raise HTTPException(
        status_code=422,
        detail="Provide either 'q' (name search) or 'upc' query parameter.",
    )
