"""
Grocery list calculator service.
Computes annual hidden cost of shrinkflation per item and in total.
"""
from __future__ import annotations

import csv
import io
from typing import Optional

from sqlalchemy.orm import Session

from app.calculations.per_unit import compute_per_unit_price
from app.models.db import Product, PricePoint, ShrinkflationEvent
from app.schemas.api import (
    GroceryItem,
    GroceryItemResult,
    GroceryListRequest,
    GroceryListResponse,
    SourceCitation,
)

BASELINE_YEAR = 2019
WEEKS_PER_YEAR = 52


def _get_per_unit_price_for_year(
    product_id: str, year: int, db: Session
) -> Optional[float]:
    """Return per-unit price for a product in a given year, or None if unavailable."""
    price_point = (
        db.query(PricePoint)
        .filter(PricePoint.product_id == product_id, PricePoint.year == year)
        .order_by(PricePoint.year.desc())
        .first()
    )
    if not price_point:
        return None

    qty_event = (
        db.query(ShrinkflationEvent)
        .filter(
            ShrinkflationEvent.product_id == product_id,
            ShrinkflationEvent.year <= year,
        )
        .order_by(ShrinkflationEvent.year.desc())
        .first()
    )
    if not qty_event or qty_event.quantity_value <= 0:
        return None

    try:
        return compute_per_unit_price(price_point.price_usd, qty_event.quantity_value)
    except ValueError:
        return None


def _get_latest_per_unit_price(product_id: str, db: Session) -> Optional[float]:
    """Return the most recent per-unit price for a product."""
    price_point = (
        db.query(PricePoint)
        .filter(PricePoint.product_id == product_id)
        .order_by(PricePoint.year.desc())
        .first()
    )
    if not price_point:
        return None

    qty_event = (
        db.query(ShrinkflationEvent)
        .filter(ShrinkflationEvent.product_id == product_id)
        .order_by(ShrinkflationEvent.year.desc())
        .first()
    )
    if not qty_event or qty_event.quantity_value <= 0:
        return None

    try:
        return compute_per_unit_price(price_point.price_usd, qty_event.quantity_value)
    except ValueError:
        return None


def calculate_grocery_list(
    request: GroceryListRequest, db: Session
) -> GroceryListResponse:
    """
    For each item in the grocery list:
    - Validate weekly_quantity in [1, 52]
    - Retrieve current and 2019-baseline per-unit prices
    - Compute annual_hidden_cost = (current - baseline) * weekly_quantity * 52
    """
    item_results: list[GroceryItemResult] = []
    total_hidden_cost = 0.0

    for item in request.items:
        if not (1 <= item.weekly_quantity <= 52):
            raise ValueError(
                f"weekly_quantity must be between 1 and 52, got {item.weekly_quantity}"
            )

        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            item_results.append(
                GroceryItemResult(
                    product_id=item.product_id,
                    product_name="Unknown Product",
                    weekly_quantity=item.weekly_quantity,
                    has_data=False,
                    no_data_message="No shrinkflation data available",
                )
            )
            continue

        baseline_price = _get_per_unit_price_for_year(item.product_id, BASELINE_YEAR, db)
        current_price = _get_latest_per_unit_price(item.product_id, db)

        if baseline_price is None or current_price is None:
            item_results.append(
                GroceryItemResult(
                    product_id=item.product_id,
                    product_name=product.name,
                    weekly_quantity=item.weekly_quantity,
                    has_data=False,
                    no_data_message="No shrinkflation data available",
                )
            )
            continue

        annual_hidden_cost = (current_price - baseline_price) * item.weekly_quantity * WEEKS_PER_YEAR
        total_hidden_cost += annual_hidden_cost

        sources = [
            SourceCitation(
                source_type="seed",
                label=f"Seed Database — {product.id}",
                source_url=None,
            )
        ]

        item_results.append(
            GroceryItemResult(
                product_id=item.product_id,
                product_name=product.name,
                weekly_quantity=item.weekly_quantity,
                baseline_per_unit_price=round(baseline_price, 4),
                current_per_unit_price=round(current_price, 4),
                annual_hidden_cost=round(annual_hidden_cost, 2),
                has_data=True,
                sources=sources,
            )
        )

    return GroceryListResponse(
        items=item_results,
        total_annual_hidden_cost=round(total_hidden_cost, 2),
    )


def export_csv(results: GroceryListResponse) -> str:
    """Generate a CSV string from grocery list results."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Product Name",
        "Weekly Quantity",
        "Baseline Per-Unit Price (2019)",
        "Current Per-Unit Price",
        "Annual Hidden Cost",
        "Source Citations",
    ])
    for item in results.items:
        citations = "; ".join(s.label for s in item.sources) if item.sources else "N/A"
        writer.writerow([
            item.product_name,
            item.weekly_quantity,
            item.baseline_per_unit_price if item.has_data else "N/A",
            item.current_per_unit_price if item.has_data else "N/A",
            item.annual_hidden_cost if item.has_data else "N/A",
            citations,
        ])
    return output.getvalue()


def export_pdf(results: GroceryListResponse) -> bytes:
    """Generate a PDF from grocery list results using fpdf2."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "ShrinkFlation Grocery List Analysis", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", size=9)
    col_widths = [55, 22, 30, 30, 30, 0]  # last col fills remaining width
    headers = [
        "Product", "Wkly Qty", "Baseline $/unit",
        "Current $/unit", "Annual Cost", "Source",
    ]

    pdf.set_fill_color(220, 220, 220)
    for i, header in enumerate(headers):
        w = col_widths[i] if col_widths[i] else pdf.w - pdf.l_margin - pdf.r_margin - sum(col_widths[:-1])
        pdf.cell(w, 7, header, border=1, fill=True)
    pdf.ln()

    pdf.set_fill_color(255, 255, 255)
    for item in results.items:
        citations = "; ".join(s.label for s in item.sources) if item.sources else "N/A"
        row = [
            item.product_name[:30],
            str(item.weekly_quantity),
            f"${item.baseline_per_unit_price:.4f}" if item.has_data and item.baseline_per_unit_price else "N/A",
            f"${item.current_per_unit_price:.4f}" if item.has_data and item.current_per_unit_price else "N/A",
            f"${item.annual_hidden_cost:.2f}" if item.has_data and item.annual_hidden_cost is not None else "N/A",
            citations[:30],
        ]
        for i, cell in enumerate(row):
            w = col_widths[i] if col_widths[i] else pdf.w - pdf.l_margin - pdf.r_margin - sum(col_widths[:-1])
            pdf.cell(w, 6, cell, border=1)
        pdf.ln()

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, f"Total Annual Hidden Cost: ${results.total_annual_hidden_cost:.2f}", ln=True)
    pdf.set_font("Helvetica", size=8)
    pdf.multi_cell(0, 5, results.methodology)

    return bytes(pdf.output())
