from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class SourceCitation(BaseModel):
    source_type: Literal["open_food_facts", "bls", "seed", "unverified"]
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    label: str
    retrieved_at: Optional[datetime] = None
    bls_vintage_date: Optional[datetime] = None


class QuantityDataPoint(BaseModel):
    year: int
    month: Optional[int] = None
    quantity_value: float
    quantity_unit: str
    is_shrinkflation_event: bool = False
    citation: SourceCitation


class PriceDataPoint(BaseModel):
    year: int
    month: Optional[int] = None
    price_usd: float
    source_type: str
    bls_series_id: Optional[str] = None
    citation: SourceCitation


class PerUnitDataPoint(BaseModel):
    year: int
    per_unit_price: float
    price_usd: float
    quantity_value: float
    quantity_unit: str


class DeceptionGapResult(BaseModel):
    gap_pp: float
    color: Literal["green", "yellow", "red"]
    per_unit_inflation_pct: float
    cpi_pct: float
    cpi_series_id: str
    cpi_date_range: tuple[int, int]
    is_fallback_cpi: bool = False


class ProductDetail(BaseModel):
    id: str
    name: str
    brand: str
    brand_id: str
    upc: Optional[str] = None
    category: Optional[str] = None
    verification_status: str
    off_last_updated: Optional[datetime] = None


class ShrinkflationReceipt(BaseModel):
    product: ProductDetail
    quantity_timeline: list[QuantityDataPoint]
    price_timeline: list[PriceDataPoint]
    per_unit_timeline: list[PerUnitDataPoint]
    deception_gap: Optional[DeceptionGapResult] = None
    cumulative_quantity_reduction_pct: Optional[float] = None
    total_per_unit_inflation_pct: Optional[float] = None
    data_last_updated: datetime
    staleness_warning: Optional[str] = None
    sources: list[SourceCitation]


class ProductSearchResult(BaseModel):
    id: str
    name: str
    brand: str
    current_quantity: Optional[float] = None
    quantity_unit: Optional[str] = None
    verification_status: Literal["verified", "unverified"]
    upc: Optional[str] = None
    category: Optional[str] = None


class SearchResponse(BaseModel):
    results: list[ProductSearchResult]
    off_unavailable: bool = False
    total: int


class ReportSubmission(BaseModel):
    product_name: str
    upc: Optional[str] = None
    brand: str
    before_quantity: float
    before_unit: str
    after_quantity: float
    after_unit: str
    change_year: int
    change_month: int
    price_at_change: Optional[float] = None


class ReportResponse(BaseModel):
    submission_id: str
    verification_status: str
    message: str


class GroceryItem(BaseModel):
    product_id: str
    weekly_quantity: int


class GroceryListRequest(BaseModel):
    items: list[GroceryItem]


class GroceryItemResult(BaseModel):
    product_id: str
    product_name: str
    weekly_quantity: int
    deception_gap: Optional[DeceptionGapResult] = None
    baseline_per_unit_price: Optional[float] = None
    current_per_unit_price: Optional[float] = None
    annual_hidden_cost: Optional[float] = None
    has_data: bool
    no_data_message: Optional[str] = None
    sources: list[SourceCitation] = []


class GroceryListResponse(BaseModel):
    items: list[GroceryItemResult]
    total_annual_hidden_cost: float
    methodology: str = "(current per-unit price − 2019 baseline per-unit price) × weekly quantity × 52 = annual hidden cost"


class BrandLeaderboardEntry(BaseModel):
    id: str
    name: str
    affected_products: int
    avg_deception_gap: Optional[float] = None
    severity_score: float
    event_count: int


class LeaderboardResponse(BaseModel):
    brands: list[BrandLeaderboardEntry]
    last_updated: datetime
    total_verified_events: int


class BrandEventDetail(BaseModel):
    product_id: str
    product_name: str
    upc: Optional[str] = None
    year: int
    quantity_before: Optional[float] = None
    quantity_after: float
    quantity_unit: str
    receipt_url: str


class BrandDetailResponse(BaseModel):
    brand: BrandLeaderboardEntry
    events: list[BrandEventDetail]


class DataSource(BaseModel):
    name: str
    description: str
    url: str
    update_frequency: str
    terms_url: str


class SourcesResponse(BaseModel):
    sources: list[DataSource]
