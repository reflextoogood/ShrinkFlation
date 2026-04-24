"""
Reports router — POST /api/v1/reports
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.schemas.api import ReportResponse, ReportSubmission
from app.services.report_service import submit_report

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post("", response_model=ReportResponse, status_code=201)
async def create_report(
    product_name: str = Form(...),
    brand: str = Form(...),
    before_quantity: float = Form(...),
    before_unit: str = Form(...),
    after_quantity: float = Form(...),
    after_unit: str = Form(...),
    change_year: int = Form(...),
    change_month: int = Form(...),
    upc: Optional[str] = Form(None),
    price_at_change: Optional[float] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    # Validate image if provided
    if image and image.filename:
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=422,
                detail=f"Image must be JPEG or PNG, got {image.content_type}",
            )
        contents = await image.read()
        if len(contents) > MAX_IMAGE_SIZE_BYTES:
            raise HTTPException(
                status_code=422,
                detail="Image must be 5 MB or smaller",
            )

    submission = ReportSubmission(
        product_name=product_name,
        upc=upc,
        brand=brand,
        before_quantity=before_quantity,
        before_unit=before_unit,
        after_quantity=after_quantity,
        after_unit=after_unit,
        change_year=change_year,
        change_month=change_month,
        price_at_change=price_at_change,
    )

    report = submit_report(submission, db)

    return ReportResponse(
        submission_id=report.submission_id,
        verification_status=report.verification_status,
        message="Report submitted successfully. It will be reviewed for verification.",
    )
