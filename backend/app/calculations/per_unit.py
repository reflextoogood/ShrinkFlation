"""
Per-unit price calculations for ShrinkFlation.

All functions are pure — no database or network I/O.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class YearlyData:
    """Intermediate struct pairing a price and quantity for a single year."""
    year: int
    price_usd: Optional[float]
    quantity_value: Optional[float]
    quantity_unit: str = ""


@dataclass
class PerUnitDataPoint:
    year: int
    per_unit_price: float
    price_usd: float
    quantity_value: float
    quantity_unit: str


def compute_per_unit_price(price: float, quantity: float) -> float:
    """
    Compute per-unit price as price / quantity.

    Raises ValueError if quantity is zero or negative.
    """
    if quantity <= 0:
        raise ValueError(f"quantity must be positive, got {quantity}")
    return price / quantity


def build_per_unit_timeline(
    price_points: list[dict],    # list of {"year": int, "price_usd": float}
    quantity_events: list[dict], # list of {"year": int, "quantity_value": float, "quantity_unit": str}
) -> list[PerUnitDataPoint]:
    """
    Build a per-unit price timeline by joining price and quantity data by year.

    Years where either price or quantity is missing are excluded from the output.
    The output is sorted ascending by year.

    price_points: list of dicts with keys "year" and "price_usd"
    quantity_events: list of dicts with keys "year", "quantity_value", "quantity_unit"
    """
    # Build lookup dicts keyed by year
    price_by_year: dict[int, float] = {}
    for pp in price_points:
        price_by_year[pp["year"]] = pp["price_usd"]

    # For quantity, if multiple events exist for the same year, use the last one
    # (most recent quantity change within that year)
    qty_by_year: dict[int, dict] = {}
    for qe in quantity_events:
        qty_by_year[qe["year"]] = qe

    # Only include years where BOTH price and quantity are present
    common_years = sorted(set(price_by_year.keys()) & set(qty_by_year.keys()))

    result: list[PerUnitDataPoint] = []
    for year in common_years:
        price = price_by_year[year]
        qty_data = qty_by_year[year]
        qty = qty_data["quantity_value"]
        unit = qty_data.get("quantity_unit", "")
        try:
            per_unit = compute_per_unit_price(price, qty)
        except ValueError:
            continue  # skip years with zero/negative quantity
        result.append(PerUnitDataPoint(
            year=year,
            per_unit_price=per_unit,
            price_usd=price,
            quantity_value=qty,
            quantity_unit=unit,
        ))

    return result


def compute_per_unit_inflation_pct(timeline: list[PerUnitDataPoint]) -> Optional[float]:
    """
    Compute total per-unit price inflation from the earliest to the most recent
    data point in the timeline.

    Formula: (last_per_unit - first_per_unit) / first_per_unit * 100

    Returns None if the timeline has fewer than 2 data points or if the first
    per-unit price is zero.
    """
    if len(timeline) < 2:
        return None
    sorted_timeline = sorted(timeline, key=lambda p: p.year)
    first = sorted_timeline[0].per_unit_price
    last = sorted_timeline[-1].per_unit_price
    if first == 0:
        return None
    return (last - first) / first * 100


def compute_cumulative_reduction_pct(quantity_events: list[dict]) -> Optional[float]:
    """
    Compute the cumulative quantity reduction percentage from the first to the
    last quantity data point.

    Formula: (first_quantity - last_quantity) / first_quantity * 100

    A positive result means the quantity decreased (shrinkflation).
    A negative result means the quantity increased.

    quantity_events: list of dicts with keys "year" and "quantity_value",
                     sorted or unsorted — this function sorts by year.

    Returns None if fewer than 2 data points or if first quantity is zero.
    """
    if len(quantity_events) < 2:
        return None
    sorted_events = sorted(quantity_events, key=lambda e: e["year"])
    first = sorted_events[0]["quantity_value"]
    last = sorted_events[-1]["quantity_value"]
    if first == 0:
        return None
    return (first - last) / first * 100
