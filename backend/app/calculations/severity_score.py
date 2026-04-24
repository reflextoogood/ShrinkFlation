"""
Brand severity score calculation for ShrinkFlation.

The severity score (0–100) ranks brands by how aggressively they practice
shrinkflation, weighting recent events more heavily.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional


RECENCY_YEARS = 3       # Events within this many years get the recency weight
RECENCY_WEIGHT = 2.0    # Multiplier for recent events
NORMAL_WEIGHT = 1.0     # Multiplier for older events


def _recency_weight(event_year: int, current_year: Optional[int] = None) -> float:
    """Return 2.0 if the event is within RECENCY_YEARS of current_year, else 1.0."""
    if current_year is None:
        current_year = datetime.utcnow().year
    return RECENCY_WEIGHT if event_year >= (current_year - RECENCY_YEARS) else NORMAL_WEIGHT


def compute_severity_score(
    events: list[dict],
    current_year: Optional[int] = None,
) -> float:
    """
    Compute a brand severity score (0–100) from a list of shrinkflation events.

    Each event dict must have:
      - "year": int
      - "quantity_reduction_pct": float  (positive = quantity decreased)

    Formula:
      raw = Σ (quantity_reduction_pct × recency_weight) for each event
      normalized to [0, 100] using a soft cap of 200 as the "maximum" raw score.

    Returns 0.0 if the events list is empty.
    """
    if not events:
        return 0.0

    if current_year is None:
        current_year = datetime.utcnow().year

    raw = sum(
        abs(e.get("quantity_reduction_pct", 0.0)) * _recency_weight(e["year"], current_year)
        for e in events
    )

    # Soft-cap normalization: 200 raw points → 100 score
    # This means a brand with 10 events each reducing quantity by 10% in recent years
    # (10 × 10% × 2.0 = 200) would score 100.
    SOFT_CAP = 200.0
    normalized = min(raw / SOFT_CAP * 100.0, 100.0)
    return round(normalized, 2)
