"""
Receipt router — GET /api/v1/receipt/{product_id}
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import ShrinkflationReceipt
from app.services.receipt_service import build_receipt

router = APIRouter(prefix="/api/v1/receipt", tags=["receipt"])


@router.get("/{product_id}", response_model=ShrinkflationReceipt)
def get_receipt(product_id: str, db: Session = Depends(get_db)):
    receipt = build_receipt(product_id, db)
    if receipt is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return receipt
