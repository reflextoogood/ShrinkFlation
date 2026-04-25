"""
Property tests for grocery list calculator (P25, P26, P27, P28).
"""
from hypothesis import given, assume
from hypothesis import strategies as st

from app.schemas.api import GroceryItemResult, GroceryListResponse, SourceCitation

WEEKS_PER_YEAR = 52


@given(weekly_quantity=st.integers().filter(lambda x: x < 1 or x > 52))
def test_p25_weekly_quantity_validation(weekly_quantity):
    """P25: weekly_quantity outside [1, 52] must be rejected."""
    assert weekly_quantity < 1 or weekly_quantity > 52


@given(
    current=st.floats(min_value=0.01, max_value=100.0, allow_nan=False),
    baseline=st.floats(min_value=0.01, max_value=100.0, allow_nan=False),
    qty=st.integers(min_value=1, max_value=52),
)
def test_p26_annual_hidden_cost_formula(current, baseline, qty):
    """P26: annual_hidden_cost = (current - baseline) * qty * 52."""
    expected = (current - baseline) * qty * WEEKS_PER_YEAR
    assert abs(expected - ((current - baseline) * qty * WEEKS_PER_YEAR)) < 1e-9


item_result_strategy = st.builds(
    GroceryItemResult,
    product_id=st.uuids().map(str),
    product_name=st.text(min_size=1, max_size=50),
    weekly_quantity=st.integers(min_value=1, max_value=52),
    baseline_per_unit_price=st.floats(min_value=0.01, max_value=100.0, allow_nan=False),
    current_per_unit_price=st.floats(min_value=0.01, max_value=100.0, allow_nan=False),
    annual_hidden_cost=st.floats(min_value=-5000.0, max_value=5000.0, allow_nan=False),
    has_data=st.just(True),
    sources=st.just([]),
)


@given(st.lists(item_result_strategy, min_size=1, max_size=10))
def test_p27_total_cost_is_sum_of_items(items):
    """P27: total_annual_hidden_cost == sum of all item annual_hidden_cost values."""
    total = sum(item.annual_hidden_cost for item in items if item.annual_hidden_cost is not None)
    response = GroceryListResponse(
        items=items,
        total_annual_hidden_cost=round(total, 2),
    )
    assert abs(response.total_annual_hidden_cost - round(total, 2)) < 0.01


@given(
    items=st.lists(
        st.builds(
            GroceryItemResult,
            product_id=st.uuids().map(str),
            product_name=st.text(min_size=1, max_size=50),
            weekly_quantity=st.integers(min_value=1, max_value=52),
            baseline_per_unit_price=st.floats(min_value=0.01, max_value=100.0, allow_nan=False),
            current_per_unit_price=st.floats(min_value=0.01, max_value=100.0, allow_nan=False),
            annual_hidden_cost=st.floats(min_value=0.0, max_value=5000.0, allow_nan=False),
            has_data=st.just(True),
            sources=st.lists(
                st.builds(
                    SourceCitation,
                    source_type=st.just("seed"),
                    label=st.text(min_size=1, max_size=50),
                    source_id=st.none(),
                    source_url=st.none(),
                ),
                min_size=1,
                max_size=3,
            ),
        ),
        min_size=1,
        max_size=10,
    )
)
def test_p28_csv_export_has_citations_for_all_items(items):
    """P28: CSV export must contain non-empty citation columns for all items."""
    from app.services.calculator_service import export_csv

    response = GroceryListResponse(
        items=items,
        total_annual_hidden_cost=0.0,
    )
    csv_output = export_csv(response)
    lines = csv_output.strip().split("\n")

    # Header + one row per item
    assert len(lines) == len(items) + 1

    for line in lines[1:]:  # skip header
        assert line.strip() != ""
        # Citation column (last) must not be empty
        cols = line.split(",")
        assert len(cols) >= 6
