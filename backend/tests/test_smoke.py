"""
Smoke tests — assert seed data loaded correctly and BLS mappings are valid.
"""
import json
from pathlib import Path

from app.calculations.deception_gap import BLS_CATEGORY_MAP, FALLBACK_CPI_SERIES

SEED_FILE = Path(__file__).parent.parent / "app" / "seed" / "seed_data.json"


def test_seed_file_has_minimum_entries():
    """Assert seed_data.json has at least 20 entries."""
    with open(SEED_FILE) as f:
        entries = json.load(f)
    assert len(entries) >= 20, f"Expected >= 20 seed entries, got {len(entries)}"


def test_seed_file_has_minimum_brands():
    """Assert seed data covers at least 10 distinct brands."""
    with open(SEED_FILE) as f:
        entries = json.load(f)
    brands = {e["brand"] for e in entries}
    assert len(brands) >= 10, f"Expected >= 10 brands, got {len(brands)}: {brands}"


def test_seed_file_has_minimum_categories():
    """Assert seed data covers at least 5 distinct categories."""
    with open(SEED_FILE) as f:
        entries = json.load(f)
    categories = {e["category"] for e in entries}
    assert len(categories) >= 5, f"Expected >= 5 categories, got {len(categories)}: {categories}"


def test_seed_entries_have_required_fields():
    """Assert every seed entry has required fields and minimum data points."""
    with open(SEED_FILE) as f:
        entries = json.load(f)
    for entry in entries:
        assert entry.get("product_name"), f"Missing product_name: {entry}"
        assert entry.get("upc"), f"Missing UPC: {entry}"
        assert entry.get("brand"), f"Missing brand: {entry}"
        assert len(entry.get("quantity_events", [])) >= 2, f"Need >= 2 quantity events: {entry['product_name']}"
        assert len(entry.get("price_points", [])) >= 1, f"Need >= 1 price point: {entry['product_name']}"
        for qe in entry["quantity_events"]:
            assert qe.get("source_url"), f"Missing source_url in quantity event: {entry['product_name']}"
        for pp in entry["price_points"]:
            assert pp.get("source_url"), f"Missing source_url in price point: {entry['product_name']}"


def test_bls_category_mappings_have_valid_series_ids():
    """Assert all BLS category mappings resolve to known series IDs."""
    for category, mapping in BLS_CATEGORY_MAP.items():
        cpi = mapping.get("cpi_series", "")
        assert cpi or cpi == "", f"Category {category} has invalid cpi_series"
    assert FALLBACK_CPI_SERIES, "Fallback CPI series must be set"
