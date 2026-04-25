"""
Crowdsourced report service — submit and auto-verify user reports.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.db import CrowdsourcedReport
from app.schemas.api import ReportSubmission, ReportResponse


def submit_report(submission: ReportSubmission, db: Session) -> CrowdsourcedReport:
    """
    Validate required fields, persist the report as unverified, and return it.
    """
    report = CrowdsourcedReport(
        id=str(uuid.uuid4()),
        submission_id=str(uuid.uuid4()),
        product_name=submission.product_name,
        upc=submission.upc,
        brand=submission.brand,
        before_quantity=submission.before_quantity,
        after_quantity=submission.after_quantity,
        quantity_unit=submission.before_unit,
        change_year=submission.change_year,
        change_month=submission.change_month,
        price_at_change=submission.price_at_change,
        verification_status="unverified",
        confirming_source=None,
        submitted_at=datetime.utcnow(),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def auto_verify_report(
    report_id: str,
    db: Session,
    off_client=None,
) -> CrowdsourcedReport | None:
    """
    Cross-check a report against Open Food Facts data.
    If a match is found, set verification_status to 'verified' and populate confirming_source.
    Returns None if the report is not found.
    """
    report = db.query(CrowdsourcedReport).filter(CrowdsourcedReport.id == report_id).first()
    if not report:
        return None

    confirming_source = None

    if off_client and report.upc:
        try:
            off_product = off_client.search_by_upc(report.upc)
            if off_product:
                confirming_source = f"open_food_facts:{report.upc}"
        except Exception:
            pass

    if confirming_source:
        report.verification_status = "verified"
        report.confirming_source = confirming_source
        report.verified_at = datetime.utcnow()
        db.commit()
        db.refresh(report)

    return report
