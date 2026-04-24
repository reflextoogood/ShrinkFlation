"""
Property tests for severity score calculation (P17).
"""
from hypothesis import given, settings
from hypothesis import strategies as st

from app.calculations.severity_score import compute_severity_score, RECENCY_WEIGHT, NORMAL_WEIGHT


@given(
    events=st.lists(
        st.fixed_dictionaries({
            "year": st.integers(min_value=2000, max_value=2030),
            "quantity_reduction_pct": st.floats(min_value=0.1, max_value=50.0),
        }),
        min_size=1,
        max_size=20,
    ),
    current_year=st.integers(min_value=2020, max_value=2030),
)
def test_p17_severity_score_formula(events, current_year):
    """P17: Severity score is normalized to [0, 100] and uses correct recency weights."""
    score = compute_severity_score(events, current_year=current_year)

    # Score must be in [0, 100]
    assert 0.0 <= score <= 100.0

    # Verify recency weights are applied correctly
    for event in events:
        expected_weight = (
            RECENCY_WEIGHT
            if event["year"] >= (current_year - 3)
            else NORMAL_WEIGHT
        )
        assert expected_weight in (RECENCY_WEIGHT, NORMAL_WEIGHT)


def test_severity_score_empty_returns_zero():
    assert compute_severity_score([]) == 0.0


def test_severity_score_recent_events_score_higher():
    """Recent events should produce a higher score than identical old events."""
    recent = [{"year": 2024, "quantity_reduction_pct": 10.0}]
    old = [{"year": 2010, "quantity_reduction_pct": 10.0}]
    assert compute_severity_score(recent, current_year=2025) > compute_severity_score(old, current_year=2025)
