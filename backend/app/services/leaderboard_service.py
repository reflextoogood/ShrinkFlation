"""
Leaderboard service — brand severity rankings.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.db import Brand, Product, ShrinkflationEvent
from app.schemas.api import (
    BrandLeaderboardEntry,
    BrandDetailResponse,
    BrandEventDetail,
    LeaderboardResponse,
)


def get_leaderboard(db: Session) -> LeaderboardResponse:
    """
    Return all brands sorted by severity_score descending.
    Each entry includes brand name, affected product count, average deception gap,
    severity score, and total verified event count.
    """
    brands = db.query(Brand).order_by(Brand.severity_score.desc()).all()

    entries: list[BrandLeaderboardEntry] = []
    for brand in brands:
        affected_products = (
            db.query(func.count(Product.id))
            .filter(Product.brand_id == brand.id)
            .scalar()
            or 0
        )
        entries.append(
            BrandLeaderboardEntry(
                id=brand.id,
                name=brand.name,
                affected_products=affected_products,
                avg_deception_gap=brand.avg_deception_gap,
                severity_score=brand.severity_score,
                event_count=brand.event_count,
            )
        )

    total_verified = (
        db.query(func.count(ShrinkflationEvent.id)).scalar() or 0
    )

    return LeaderboardResponse(
        brands=entries,
        last_updated=datetime.utcnow(),
        total_verified_events=total_verified,
    )


def get_brand_detail(brand_id: str, db: Session) -> BrandDetailResponse | None:
    """
    Return a brand's detail including only verified shrinkflation events,
    each with a link to the product receipt.
    Returns None if the brand is not found.
    """
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        return None

    affected_products = (
        db.query(func.count(Product.id))
        .filter(Product.brand_id == brand.id)
        .scalar()
        or 0
    )

    brand_entry = BrandLeaderboardEntry(
        id=brand.id,
        name=brand.name,
        affected_products=affected_products,
        avg_deception_gap=brand.avg_deception_gap,
        severity_score=brand.severity_score,
        event_count=brand.event_count,
    )

    # Fetch all events for products belonging to this brand
    events_query = (
        db.query(ShrinkflationEvent, Product)
        .join(Product, ShrinkflationEvent.product_id == Product.id)
        .filter(Product.brand_id == brand_id)
        .order_by(ShrinkflationEvent.year.desc())
        .all()
    )

    event_details: list[BrandEventDetail] = []
    for event, product in events_query:
        # Get the previous event for this product to determine quantity_before
        prev_event = (
            db.query(ShrinkflationEvent)
            .filter(
                ShrinkflationEvent.product_id == product.id,
                ShrinkflationEvent.year < event.year,
            )
            .order_by(ShrinkflationEvent.year.desc())
            .first()
        )
        quantity_before = prev_event.quantity_value if prev_event else None

        event_details.append(
            BrandEventDetail(
                product_id=product.id,
                product_name=product.name,
                upc=product.upc,
                year=event.year,
                quantity_before=quantity_before,
                quantity_after=event.quantity_value,
                quantity_unit=event.quantity_unit,
                receipt_url=f"/api/v1/receipt/{product.id}",
            )
        )

    return BrandDetailResponse(brand=brand_entry, events=event_details)
