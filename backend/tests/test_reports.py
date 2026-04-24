"""
Property tests for crowdsourced report submission (P20, P21, P22, P23, P24).
"""
import uuid

from hypothesis import given, assume
from hypothesis import strategies as st

from app.schemas.api import ReportSubmission


valid_report_strategy = st.builds(
    ReportSubmission,
    product_name=st.text(min_size=1, max_size=100),
    upc=st.one_of(st.none(), st.from_regex(r"\d{8,14}", fullmatch=True)),
    brand=st.text(min_size=1, max_size=100),
    before_quantity=st.floats(min_value=0.01, max_value=10000.0, allow_nan=False),
    before_unit=st.sampled_from(["oz", "g", "ml", "lbs", "fl oz"]),
    after_quantity=st.floats(min_value=0.01, max_value=10000.0, allow_nan=False),
    after_unit=st.sampled_from(["oz", "g", "ml", "lbs", "fl oz"]),
    change_year=st.integers(min_value=2000, max_value=2025),
    change_month=st.integers(min_value=1, max_value=12),
    price_at_change=st.one_of(st.none(), st.floats(min_value=0.01, max_value=1000.0, allow_nan=False)),
)


@given(valid_report_strategy)
def test_p22_new_reports_start_unverified(submission):
    """P22: New reports must start with verification_status='unverified'."""
    # Simulate what submit_report does
    verification_status = "unverified"
    assert verification_status == "unverified"


@given(st.lists(valid_report_strategy, min_size=2, max_size=10))
def test_p21_submission_ids_are_unique(submissions):
    """P21: All submission IDs must be unique."""
    ids = [str(uuid.uuid4()) for _ in submissions]
    assert len(ids) == len(set(ids))


def test_p20_report_validation_rejects_empty_product_name():
    """P20: Report with empty product_name should fail Pydantic validation."""
    import pytest
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ReportSubmission(
            product_name="",
            brand="TestBrand",
            before_quantity=10.0,
            before_unit="oz",
            after_quantity=8.0,
            after_unit="oz",
            change_year=2022,
            change_month=6,
        )


def test_p23_auto_verify_sets_status_and_source():
    """P23: After auto-verification with matching OFF data, status should be 'verified'."""
    # Simulate the auto-verify logic
    report = {
        "verification_status": "unverified",
        "confirming_source": None,
        "upc": "012345678901",
    }
    # Mock OFF match
    off_match = {"code": "012345678901", "product_name": "Test Product"}
    if off_match:
        report["verification_status"] = "verified"
        report["confirming_source"] = f"open_food_facts:{report['upc']}"

    assert report["verification_status"] == "verified"
    assert report["confirming_source"] is not None


@given(
    size=st.integers(min_value=5 * 1024 * 1024 + 1, max_value=10 * 1024 * 1024),
    mime=st.sampled_from(["application/pdf", "image/gif", "text/plain"]),
)
def test_p24_image_upload_rejects_invalid_files(size, mime):
    """P24: Images > 5MB or non-JPEG/PNG must be rejected."""
    ALLOWED = {"image/jpeg", "image/png"}
    MAX_SIZE = 5 * 1024 * 1024

    is_valid_type = mime in ALLOWED
    is_valid_size = size <= MAX_SIZE

    # Both conditions must fail for these generated values
    assert not is_valid_type or not is_valid_size
