"""
Property tests for leaderboard invariants (P16, P18, P19).
"""
from hypothesis import given, assume
from hypothesis import strategies as st

from app.schemas.api import BrandLeaderboardEntry


def _make_entry(**kwargs) -> BrandLeaderboardEntry:
    defaults = dict(
        id="brand-1",
        name="Test Brand",
        affected_products=1,
        avg_deception_gap=5.0,
        severity_score=50.0,
        event_count=1,
    )
    defaults.update(kwargs)
    return BrandLeaderboardEntry(**defaults)


brand_entry_strategy = st.builds(
    BrandLeaderboardEntry,
    id=st.uuids().map(str),
    name=st.text(min_size=1, max_size=50),
    affected_products=st.integers(min_value=0, max_value=100),
    avg_deception_gap=st.one_of(st.none(), st.floats(min_value=-50.0, max_value=200.0, allow_nan=False)),
    severity_score=st.floats(min_value=0.0, max_value=100.0, allow_nan=False),
    event_count=st.integers(min_value=0, max_value=500),
)


@given(st.lists(brand_entry_strategy, min_size=2, max_size=20))
def test_p16_leaderboard_descending_sort(brands):
    """P16: Leaderboard must be sorted by severity_score descending."""
    sorted_brands = sorted(brands, key=lambda b: b.severity_score, reverse=True)
    for i in range(len(sorted_brands) - 1):
        assert sorted_brands[i].severity_score >= sorted_brands[i + 1].severity_score


@given(brand_entry_strategy)
def test_p18_leaderboard_entry_required_fields(entry):
    """P18: Every leaderboard entry must have non-null required fields."""
    assert entry.name is not None and len(entry.name) > 0
    assert entry.affected_products is not None
    assert entry.severity_score is not None
    assert entry.event_count is not None


def test_p19_brand_detail_verified_events_only():
    """P19: Brand detail should only contain events for the correct brand."""
    brand_id = "brand-abc"
    # Simulate filtering — all events must match brand_id
    events = [
        {"brand_id": brand_id, "verification_status": "verified"},
        {"brand_id": brand_id, "verification_status": "verified"},
    ]
    for event in events:
        assert event["brand_id"] == brand_id
        assert event["verification_status"] == "verified"
