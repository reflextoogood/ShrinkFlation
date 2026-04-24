"""
Deception gap calculation for ShrinkFlation.

The deception gap measures how much worse a product's true per-unit price
inflation is compared to the official CPI for the same food category.
"""
from __future__ import annotations

from typing import Optional

# BLS series mapping: food category → (average price series, CPI series)
# Sources:
#   Average price series: https://www.bls.gov/cpi/tables/average-price-data.htm
#   CPI series: https://www.bls.gov/cpi/
BLS_CATEGORY_MAP: dict[str, dict[str, str]] = {
    "cereals": {
        "avg_price_series": "APU0000702111",   # White bread, per lb
        "cpi_series": "CUUR0000SAF111",         # Cereals and bakery products
    },
    "bakery": {
        "avg_price_series": "APU0000702111",
        "cpi_series": "CUUR0000SAF111",
    },
    "snacks": {
        "avg_price_series": "APU0000718311",    # Potato chips
        "cpi_series": "CUUR0000SAF1",           # Food at home
    },
    "chips": {
        "avg_price_series": "APU0000718311",
        "cpi_series": "CUUR0000SAF1",
    },
    "beverages": {
        "avg_price_series": "APU0000712311",    # Orange juice, per 16 oz
        "cpi_series": "CUUR0000SAF116",         # Nonalcoholic beverages
    },
    "drinks": {
        "avg_price_series": "APU0000712311",
        "cpi_series": "CUUR0000SAF116",
    },
    "dairy": {
        "avg_price_series": "APU0000710212",    # Whole milk, per gallon
        "cpi_series": "CUUR0000SAF112",         # Dairy and related products
    },
    "household": {
        "avg_price_series": "",                  # No BLS average price series
        "cpi_series": "CUUR0000SAH",            # Household furnishings and operations
    },
    "household goods": {
        "avg_price_series": "",
        "cpi_series": "CUUR0000SAH",
    },
    "candy": {
        "avg_price_series": "",
        "cpi_series": "CUUR0000SAF1",
    },
    "frozen": {
        "avg_price_series": "",
        "cpi_series": "CUUR0000SAF1",
    },
    "condiments": {
        "avg_price_series": "",
        "cpi_series": "CUUR0000SAF1",
    },
    "pasta": {
        "avg_price_series": "",
        "cpi_series": "CUUR0000SAF111",
    },
}

# Fallback: overall food CPI
FALLBACK_CPI_SERIES = "CUUR0000SAF"


def get_cpi_series_for_category(category: str) -> tuple[str, bool]:
    """
    Return the BLS CPI series ID for a given food category.

    Returns a tuple of (series_id, is_fallback).
    - is_fallback=False means a category-specific series was found.
    - is_fallback=True means the overall food CPI fallback is being used.

    The category lookup is case-insensitive and strips whitespace.
    """
    normalized = category.strip().lower() if category else ""
    mapping = BLS_CATEGORY_MAP.get(normalized)
    if mapping and mapping["cpi_series"]:
        return mapping["cpi_series"], False
    return FALLBACK_CPI_SERIES, True


def _classify_color(gap_pp: float) -> str:
    """
    Classify a deception gap value into a color tier.

    green:  0 ≤ gap ≤ 10 pp above CPI
    yellow: 11 ≤ gap ≤ 25 pp above CPI
    red:    gap > 25 pp above CPI

    Values below 0 (product inflation lower than CPI) are classified green.
    """
    if gap_pp <= 10:
        return "green"
    elif gap_pp <= 25:
        return "yellow"
    else:
        return "red"


def compute_deception_gap(
    per_unit_inflation_pct: float,
    cpi_pct: float,
    cpi_series_id: str,
    cpi_date_range: tuple[int, int],
    is_fallback_cpi: bool = False,
) -> dict:
    """
    Compute the deception gap between per-unit price inflation and CPI.

    Formula: gap_pp = per_unit_inflation_pct - cpi_pct

    Returns a dict matching the DeceptionGapResult Pydantic schema:
    {
        "gap_pp": float,
        "color": "green" | "yellow" | "red",
        "per_unit_inflation_pct": float,
        "cpi_pct": float,
        "cpi_series_id": str,
        "cpi_date_range": (start_year, end_year),
        "is_fallback_cpi": bool,
    }
    """
    gap_pp = per_unit_inflation_pct - cpi_pct
    color = _classify_color(gap_pp)
    return {
        "gap_pp": round(gap_pp, 2),
        "color": color,
        "per_unit_inflation_pct": round(per_unit_inflation_pct, 2),
        "cpi_pct": round(cpi_pct, 2),
        "cpi_series_id": cpi_series_id,
        "cpi_date_range": cpi_date_range,
        "is_fallback_cpi": is_fallback_cpi,
    }
