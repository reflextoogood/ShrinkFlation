"""
Search service — merges seed DB results with Open Food Facts results.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.db import Product, ShrinkflationEvent
from app.schemas.api import ProductSearchResult, SearchResponse
from app.services.off_client import OFFUnavailableError, search_by_name, search_by_upc


def _product_to_result(product: Product, db: Session) -> ProductSearchResult:
    latest_event = (
        db.query(ShrinkflationEvent)
        .filter(ShrinkflationEvent.product_id == product.id)
        .order_by(ShrinkflationEvent.year.desc())
        .first()
    )
    return ProductSearchResult(
        id=product.id,
        name=product.name,
        brand=product.brand_rel.name if product.brand_rel else "Unknown",
        current_quantity=latest_event.quantity_value if latest_event else None,
        quantity_unit=latest_event.quantity_unit if latest_event else None,
        verification_status=product.verification_status,  # type: ignore
        upc=product.upc,
        category=product.category,
    )


def _off_to_result(off_product: dict) -> ProductSearchResult:
    return ProductSearchResult(
        id=off_product.get("id", off_product.get("code", "")),
        name=off_product.get("product_name", "Unknown"),
        brand=off_product.get("brands", "Unknown"),
        current_quantity=None,
        quantity_unit=None,
        verification_status="unverified",
        upc=off_product.get("code"),
        category=off_product.get("categories", ""),
    )


def search_products(
    query: str, db: Session
) -> SearchResponse:
    """
    Search by product name. Merges seed DB + OFF results, deduplicates by UPC.
    Falls back to seed-only if OFF is unavailable.
    """
    off_unavailable = False
    results: dict[str, ProductSearchResult] = {}

    # Seed DB search
    seed_products = (
        db.query(Product)
        .filter(Product.name.ilike(f"%{query}%"))
        .limit(20)
        .all()
    )
    for p in seed_products:
        result = _product_to_result(p, db)
        key = p.upc or p.id
        results[key] = result

    # OFF search
    try:
        off_products = search_by_name(query)
        for op in off_products:
            upc = op.get("code", "")
            if upc and upc in results:
                continue  # seed result takes priority
            result = _off_to_result(op)
            results[upc or result.id] = result
    except OFFUnavailableError:
        off_unavailable = True

    return SearchResponse(
        results=list(results.values()),
        off_unavailable=off_unavailable,
        total=len(results),
    )


def search_by_upc_service(
    upc: str, db: Session
) -> tuple[Optional[ProductSearchResult], bool]:
    """
    Search by UPC. Returns (result, off_unavailable).
    Seed DB takes priority over OFF.
    """
    off_unavailable = False

    seed_product = db.query(Product).filter(Product.upc == upc).first()
    if seed_product:
        return _product_to_result(seed_product, db), False

    try:
        off_product = search_by_upc(upc)
        if off_product:
            return _off_to_result(off_product), False
    except OFFUnavailableError:
        off_unavailable = True

    return None, off_unavailable
