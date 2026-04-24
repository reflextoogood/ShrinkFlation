"""
Receipt service — assembles a full ShrinkflationReceipt for a product.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.calculations.deception_gap import compute_deception_gap, get_cpi_series_for_category
from app.calculations.per_unit import (
    build_per_unit_timeline,
    compute_cumulative_reduction_pct,
    compute_per_unit_inflation_pct,
)
from app.models.db import Product, ShrinkflationEvent, PricePoint
from app.schemas.api import (
    DeceptionGapResult,
    PerUnitDataPoint,
    PriceDataPoint,
    ProductDetail,
    QuantityDataPoint,
    ShrinkflationReceipt,
    SourceCitation,
)
from app.services.bls_client import BLSUnavailableError, fetch_bls_series

STALENESS_DAYS = 180


def _make_seed_citation(source_url: Optional[str], entry_id: str) -> SourceCitation:
    return SourceCitation(
        source_type="seed",
        source_id=entry_id,
        source_url=source_url,
        label=f"Seed Database — {entry_id}",
    )


def build_receipt(
    product_id: str,
    db: Session,
    bls_client=None,
) -> Optional[ShrinkflationReceipt]:
    """
    Assemble a full ShrinkflationReceipt for a product.
    Returns None if the product is not found.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    brand_name = product.brand_rel.name if product.brand_rel else "Unknown"

    # --- Quantity timeline ---
    events = (
        db.query(ShrinkflationEvent)
        .filter(ShrinkflationEvent.product_id == product_id)
        .order_by(ShrinkflationEvent.year)
        .all()
    )

    quantity_timeline: list[QuantityDataPoint] = []
    qty_dicts: list[dict] = []
    for i, ev in enumerate(events):
        is_shrink = i > 0 and ev.quantity_value < events[i - 1].quantity_value
        citation = _make_seed_citation(ev.source_url, ev.id)
        quantity_timeline.append(QuantityDataPoint(
            year=ev.year,
            month=ev.month,
            quantity_value=ev.quantity_value,
            quantity_unit=ev.quantity_unit,
            is_shrinkflation_event=is_shrink,
            citation=citation,
        ))
        qty_dicts.append({"year": ev.year, "quantity_value": ev.quantity_value, "quantity_unit": ev.quantity_unit})

    # --- Price timeline (BLS preferred, seed fallback) ---
    seed_prices = (
        db.query(PricePoint)
        .filter(PricePoint.product_id == product_id)
        .order_by(PricePoint.year)
        .all()
    )

    price_timeline: list[PriceDataPoint] = []
    price_dicts: list[dict] = []
    bls_vintage_date: Optional[datetime] = None
    bls_unavailable = False

    # Try BLS prices
    if product.category and bls_client is not None:
        cpi_series_id, is_fallback = get_cpi_series_for_category(product.category)
        try:
            bls_data = fetch_bls_series(
                cpi_series_id,
                start_year=2005,
                end_year=datetime.utcnow().year,
                db=db,
            )
            for item in bls_data:
                citation = SourceCitation(
                    source_type="bls",
                    source_id=cpi_series_id,
                    source_url=f"https://www.bls.gov/cpi/",
                    label=f"BLS {cpi_series_id}",
                    bls_vintage_date=bls_vintage_date,
                )
                price_timeline.append(PriceDataPoint(
                    year=item["year"],
                    price_usd=item["value"],
                    source_type="bls",
                    bls_series_id=cpi_series_id,
                    citation=citation,
                ))
                price_dicts.append({"year": item["year"], "price_usd": item["value"]})
        except BLSUnavailableError:
            bls_unavailable = True

    # Fall back to seed prices
    if not price_timeline:
        for pp in seed_prices:
            citation = _make_seed_citation(pp.source_url, pp.id)
            price_timeline.append(PriceDataPoint(
                year=pp.year,
                month=pp.month,
                price_usd=pp.price_usd,
                source_type="seed",
                citation=citation,
            ))
            price_dicts.append({"year": pp.year, "price_usd": pp.price_usd})

    # --- Per-unit timeline ---
    raw_per_unit = build_per_unit_timeline(price_dicts, qty_dicts)
    per_unit_timeline = [
        PerUnitDataPoint(
            year=p.year,
            per_unit_price=p.per_unit_price,
            price_usd=p.price_usd,
            quantity_value=p.quantity_value,
            quantity_unit=p.quantity_unit,
        )
        for p in raw_per_unit
    ]

    # --- Deception gap ---
    deception_gap: Optional[DeceptionGapResult] = None
    per_unit_inflation = compute_per_unit_inflation_pct(raw_per_unit)
    if per_unit_inflation is not None and product.category:
        cpi_series_id, is_fallback = get_cpi_series_for_category(product.category)
        # Use a placeholder CPI of 30% over the period as a seed fallback
        cpi_pct = 30.0
        gap_dict = compute_deception_gap(
            per_unit_inflation_pct=per_unit_inflation,
            cpi_pct=cpi_pct,
            cpi_series_id=cpi_series_id,
            cpi_date_range=(
                raw_per_unit[0].year if raw_per_unit else 2010,
                raw_per_unit[-1].year if raw_per_unit else 2023,
            ),
            is_fallback_cpi=is_fallback,
        )
        deception_gap = DeceptionGapResult(**gap_dict)

    # --- Cumulative reduction ---
    cumulative_reduction = compute_cumulative_reduction_pct(qty_dicts) if qty_dicts else None

    # --- Staleness warning ---
    staleness_warning: Optional[str] = None
    if product.off_last_updated:
        age = datetime.utcnow() - product.off_last_updated
        if age.days > STALENESS_DAYS:
            staleness_warning = f"Data may be outdated — last updated {age.days} days ago."

    # --- Sources ---
    all_sources: list[SourceCitation] = []
    for qt in quantity_timeline:
        all_sources.append(qt.citation)
    for pt in price_timeline:
        all_sources.append(pt.citation)

    return ShrinkflationReceipt(
        product=ProductDetail(
            id=product.id,
            name=product.name,
            brand=brand_name,
            brand_id=product.brand_id,
            upc=product.upc,
            category=product.category,
            verification_status=product.verification_status,
            off_last_updated=product.off_last_updated,
        ),
        quantity_timeline=quantity_timeline,
        price_timeline=price_timeline,
        per_unit_timeline=per_unit_timeline,
        deception_gap=deception_gap,
        cumulative_quantity_reduction_pct=cumulative_reduction,
        total_per_unit_inflation_pct=per_unit_inflation,
        data_last_updated=datetime.utcnow(),
        staleness_warning=staleness_warning,
        sources=all_sources,
    )
