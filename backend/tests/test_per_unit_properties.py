"""
Property tests for per-unit calculations (P9, P10, P11) and cumulative reduction (P6).
"""
from hypothesis import given, assume
from hypothesis import strategies as st

from app.calculations.per_unit import (
    compute_per_unit_price,
    build_per_unit_timeline,
    compute_per_unit_inflation_pct,
    compute_cumulative_reduction_pct,
    YearlyData,
)


@given(
    price=st.floats(min_value=0.01, max_value=10000.0, allow_nan=False),
    quantity=st.floats(min_value=0.01, max_value=10000.0, allow_nan=False),
)
def test_p9_per_unit_price_formula(price, quantity):
    """P9: per_unit_price == price / quantity within float tolerance."""
    result = compute_per_unit_price(price, quantity)
    assert abs(result - price / quantity) < 1e-9


@given(
    rows=st.lists(
        st.fixed_dictionaries({
            "year": st.integers(min_value=2000, max_value=2030),
            "price_usd": st.one_of(st.none(), st.floats(min_value=0.01, max_value=1000.0, allow_nan=False)),
            "quantity_value": st.one_of(st.none(), st.floats(min_value=0.01, max_value=1000.0, allow_nan=False)),
            "quantity_unit": st.just("oz"),
        }),
        min_size=0,
        max_size=10,
    )
)
def test_p10_per_unit_timeline_excludes_incomplete_years(rows):
    """P10: Timeline excludes years where price or quantity is missing."""
    price_points = [{"year": r["year"], "price_usd": r["price_usd"]} for r in rows if r["price_usd"] is not None]
    qty_events = [{"year": r["year"], "quantity_value": r["quantity_value"], "quantity_unit": r["quantity_unit"]} for r in rows if r["quantity_value"] is not None]

    timeline = build_per_unit_timeline(price_points, qty_events)

    price_years = {p["year"] for p in price_points}
    qty_years = {q["year"] for q in qty_events}
    valid_years = price_years & qty_years

    for point in timeline:
        assert point.year in valid_years


@given(
    values=st.lists(st.floats(min_value=0.01, max_value=1000.0, allow_nan=False), min_size=2, max_size=10)
)
def test_p11_per_unit_inflation_formula(values):
    """P11: inflation_pct == (last - first) / first * 100."""
    from app.calculations.per_unit import PerUnitDataPoint
    timeline = [
        PerUnitDataPoint(year=2000 + i, per_unit_price=v, price_usd=v, quantity_value=1.0, quantity_unit="oz")
        for i, v in enumerate(values)
    ]
    result = compute_per_unit_inflation_pct(timeline)
    first = values[0]
    last = values[-1]
    expected = (last - first) / first * 100
    assert result is not None
    assert abs(result - expected) < 1e-6


@given(
    values=st.lists(st.floats(min_value=0.1, max_value=1000.0, allow_nan=False), min_size=2, max_size=10)
)
def test_p6_cumulative_reduction_formula(values):
    """P6: cumulative_reduction == (first - last) / first * 100."""
    events = [{"year": 2000 + i, "quantity_value": v} for i, v in enumerate(values)]
    result = compute_cumulative_reduction_pct(events)
    first = values[0]
    last = values[-1]
    expected = (first - last) / first * 100
    assert result is not None
    assert abs(result - expected) < 1e-6
