"""
LangGraph tool definitions for the ShrinkFlation Detective Agent.
Each tool wraps existing services so the agent can call them autonomously.
"""
from __future__ import annotations

import json
from typing import Optional

from langchain_core.tools import tool

from app.calculations.deception_gap import compute_deception_gap, get_cpi_series_for_category
from app.calculations.per_unit import (
    build_per_unit_timeline,
    compute_cumulative_reduction_pct,
    compute_per_unit_inflation_pct,
)
from app.db.session import SessionLocal
from app.models.db import Brand, Product, ShrinkflationEvent, PricePoint
from app.services.off_client import search_by_name, search_by_upc, OFFUnavailableError


@tool
def search_product_in_db(query: str) -> str:
    """
    Search the ShrinkFlation seed database for products matching the query.
    Returns a JSON list of matching products with their IDs, names, brands, and categories.
    Use this first to check if we already have data on a product.
    """
    db = SessionLocal()
    try:
        products = (
            db.query(Product)
            .filter(Product.name.ilike(f"%{query}%"))
            .limit(5)
            .all()
        )
        results = [
            {
                "id": p.id,
                "name": p.name,
                "brand": p.brand_rel.name if p.brand_rel else "Unknown",
                "category": p.category,
                "upc": p.upc,
                "verification_status": p.verification_status,
            }
            for p in products
        ]
        return json.dumps(results) if results else "No products found in database."
    finally:
        db.close()


@tool
def get_quantity_history(product_id: str) -> str:
    """
    Get the full quantity history for a product by its ID.
    Returns a JSON list of shrinkflation events showing how the quantity changed over time.
    Use this to understand how much a product has shrunk.
    """
    db = SessionLocal()
    try:
        events = (
            db.query(ShrinkflationEvent)
            .filter(ShrinkflationEvent.product_id == product_id)
            .order_by(ShrinkflationEvent.year)
            .all()
        )
        if not events:
            return "No quantity history found for this product."
        result = [
            {
                "year": e.year,
                "quantity_value": e.quantity_value,
                "quantity_unit": e.quantity_unit,
                "source_url": e.source_url,
            }
            for e in events
        ]
        return json.dumps(result)
    finally:
        db.close()


@tool
def get_price_history(product_id: str) -> str:
    """
    Get the price history for a product by its ID.
    Returns a JSON list of price points over the years.
    Use this to calculate per-unit price inflation.
    """
    db = SessionLocal()
    try:
        prices = (
            db.query(PricePoint)
            .filter(PricePoint.product_id == product_id)
            .order_by(PricePoint.year)
            .all()
        )
        if not prices:
            return "No price history found for this product."
        result = [
            {"year": p.year, "price_usd": p.price_usd, "source_type": p.source_type}
            for p in prices
        ]
        return json.dumps(result)
    finally:
        db.close()


@tool
def calculate_shrinkflation_metrics(product_id: str) -> str:
    """
    Calculate all shrinkflation metrics for a product: per-unit price inflation,
    cumulative quantity reduction, and deception gap vs CPI.
    Returns a JSON summary of the analysis.
    Use this after getting quantity and price history to compute the final verdict.
    """
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return "Product not found."

        events = (
            db.query(ShrinkflationEvent)
            .filter(ShrinkflationEvent.product_id == product_id)
            .order_by(ShrinkflationEvent.year)
            .all()
        )
        prices = (
            db.query(PricePoint)
            .filter(PricePoint.product_id == product_id)
            .order_by(PricePoint.year)
            .all()
        )

        qty_dicts = [{"year": e.year, "quantity_value": e.quantity_value, "quantity_unit": e.quantity_unit} for e in events]
        price_dicts = [{"year": p.year, "price_usd": p.price_usd} for p in prices]

        timeline = build_per_unit_timeline(price_dicts, qty_dicts)
        per_unit_inflation = compute_per_unit_inflation_pct(timeline)
        cumulative_reduction = compute_cumulative_reduction_pct(qty_dicts)

        deception_gap = None
        if per_unit_inflation is not None and product.category:
            cpi_series_id, is_fallback = get_cpi_series_for_category(product.category)
            cpi_pct = 30.0  # baseline CPI estimate
            gap = compute_deception_gap(
                per_unit_inflation_pct=per_unit_inflation,
                cpi_pct=cpi_pct,
                cpi_series_id=cpi_series_id,
                cpi_date_range=(
                    timeline[0].year if timeline else 2010,
                    timeline[-1].year if timeline else 2023,
                ),
                is_fallback_cpi=is_fallback,
            )
            deception_gap = gap

        return json.dumps({
            "product_name": product.name,
            "brand": product.brand_rel.name if product.brand_rel else "Unknown",
            "category": product.category,
            "per_unit_inflation_pct": round(per_unit_inflation, 2) if per_unit_inflation else None,
            "cumulative_quantity_reduction_pct": round(cumulative_reduction, 2) if cumulative_reduction else None,
            "deception_gap": deception_gap,
            "quantity_events_count": len(events),
            "price_points_count": len(prices),
        })
    finally:
        db.close()


@tool
def search_open_food_facts(query: str) -> str:
    """
    Search Open Food Facts for a product by name.
    Returns product data including quantity, brand, and nutritional info.
    Use this to find external verification of product sizes.
    """
    try:
        results = search_by_name(query)
        if not results:
            return "No results found on Open Food Facts."
        simplified = [
            {
                "name": r.get("product_name", "Unknown"),
                "brand": r.get("brands", "Unknown"),
                "quantity": r.get("quantity", "Unknown"),
                "upc": r.get("code", ""),
                "categories": r.get("categories", ""),
            }
            for r in results[:3]
        ]
        return json.dumps(simplified)
    except OFFUnavailableError:
        return "Open Food Facts is currently unavailable."


@tool
def get_brand_severity(brand_name: str) -> str:
    """
    Get the severity score and shrinkflation history for a brand.
    Returns the brand's severity score (0-100), affected product count, and event count.
    Use this to assess how bad a brand's shrinkflation practices are overall.
    """
    db = SessionLocal()
    try:
        brand = db.query(Brand).filter(Brand.name.ilike(f"%{brand_name}%")).first()
        if not brand:
            return f"Brand '{brand_name}' not found in database."
        return json.dumps({
            "brand_name": brand.name,
            "severity_score": brand.severity_score,
            "event_count": brand.event_count,
            "avg_deception_gap": brand.avg_deception_gap,
        })
    finally:
        db.close()


# All tools available to the agent
AGENT_TOOLS = [
    search_product_in_db,
    get_quantity_history,
    get_price_history,
    calculate_shrinkflation_metrics,
    search_open_food_facts,
    get_brand_severity,
]
