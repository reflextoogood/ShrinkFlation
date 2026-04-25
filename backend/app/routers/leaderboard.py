"""
Leaderboard router — GET /api/v1/leaderboard
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import LeaderboardResponse, BrandDetailResponse
from app.services.leaderboard_service import get_leaderboard, get_brand_detail

router = APIRouter(prefix="/api/v1/leaderboard", tags=["leaderboard"])


@router.get("", response_model=LeaderboardResponse)
def leaderboard(db: Session = Depends(get_db)):
    return get_leaderboard(db)


@router.get("/{brand_id}", response_model=BrandDetailResponse)
def brand_detail(brand_id: str, db: Session = Depends(get_db)):
    result = get_brand_detail(brand_id, db)
    if result is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return result
