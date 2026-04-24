"""
Property tests for deception gap calculations (P12, P13).
"""
from hypothesis import given
from hypothesis import strategies as st

from app.calculations.deception_gap import compute_deception_gap, _classify_color


@given(
    per_unit_inflation=st.floats(min_value=-100.0, max_value=500.0, allow_nan=False),
    cpi=st.floats(min_value=-50.0, max_value=200.0, allow_nan=False),
)
def test_p12_deception_gap_formula(per_unit_inflation, cpi):
    """P12: gap_pp == per_unit_inflation_pct - cpi_pct."""
    result = compute_deception_gap(
        per_unit_inflation_pct=per_unit_inflation,
        cpi_pct=cpi,
        cpi_series_id="CUUR0000SAF",
        cpi_date_range=(2010, 2023),
    )
    assert abs(result["gap_pp"] - round(per_unit_inflation - cpi, 2)) < 0.01


@given(gap=st.floats(min_value=0.0, max_value=200.0, allow_nan=False))
def test_p13_deception_gap_color_thresholds(gap):
    """P13: Color thresholds are exactly green ≤10, yellow 11–25, red >25."""
    color = _classify_color(gap)
    if gap <= 10:
        assert color == "green"
    elif gap <= 25:
        assert color == "yellow"
    else:
        assert color == "red"


def test_deception_gap_negative_is_green():
    """Values below 0 (product inflation lower than CPI) should be green."""
    color = _classify_color(-5.0)
    assert color == "green"
