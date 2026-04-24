# Implementation Plan: ShrinkFlation

## Team Assignments

| Person | Name   | Role                        |
|--------|--------|-----------------------------|
| A      | Deepak | Backend Foundation          |
| B      | Aneesh | Backend Features & Tests    |
| C      | Vijay  | Frontend                    |

## Overview

Tasks are sequenced for the fastest path to a working demo: seed data first, then one end-to-end Shrinkflation Receipt (backend + frontend), then the remaining features (Brand Leaderboard, Crowdsourced Reporting, Grocery Calculator), and finally tests and polish. Infrastructure is kept minimal — just enough to run each feature as it is added.

---

## Tasks

- [x] 1. Minimal project scaffolding <!-- Deepak -->
  - Create `backend/` directory with `app/main.py` (FastAPI app with CORS, health endpoint), `app/db/session.py` (SQLite engine + session factory), `app/models/db.py` (SQLAlchemy ORM models for Product, Brand, ShrinkflationEvent, PricePoint, CrowdsourcedReport, BLSCache), and `requirements.txt` pinning FastAPI, SQLAlchemy, Pydantic, Hypothesis, pytest, httpx, python-multipart
  - Create `frontend/` directory with a Vite + React + TypeScript scaffold (`npm create vite`), install recharts, and add `src/api/client.ts` as a typed fetch wrapper pointing to `http://localhost:8000`
  - Wire `app/main.py` to create all DB tables on startup via `Base.metadata.create_all`
  - _Requirements: 1.1, 2.1, 11.1_

- [x] 2. Seed database with real shrinkflation data <!-- Deepak -->
  - Create `app/seed/seed_data.json` containing 20–30 verified shrinkflation examples covering at least 10 brands and 5 grocery categories (snacks, beverages, dairy, cereals, household goods); each entry must include product name, UPC, brand, at least 2 quantity data points with dates, at least 1 price data point, and a source citation URL per data point
  - Write `app/seed/loader.py` that reads `seed_data.json` and upserts Products, Brands, ShrinkflationEvents, and PricePoints into SQLite on app startup; call it from the FastAPI `startup` event in `main.py`
  - Write a build-time script `scripts/check_seed_urls.py` that HTTP-checks every source URL in `seed_data.json` and prints a report of broken links
  - _Requirements: 11.1, 11.2, 11.3, 11.4_

- [ ] 3. Checkpoint — seed data loads cleanly <!-- Deepak -->
  - Ensure all tests pass, ask the user if questions arise.

- [-] 4. Backend: Shrinkflation Receipt calculation engine <!-- Deepak -->
  - [x] 4.1 Implement per-unit price calculation in `app/calculations/per_unit.py`
    - Write `compute_per_unit_price(price: float, quantity: float) -> float` and `build_per_unit_timeline(price_points, quantity_events) -> list[PerUnitDataPoint]` that excludes years with missing price or quantity
    - Write `compute_per_unit_inflation_pct(timeline: list[PerUnitDataPoint]) -> float` using earliest-to-latest formula
    - _Requirements: 5.1, 5.3, 5.5_

  - [ ]* 4.2 Write property tests for per-unit calculations (P9, P10, P11) <!-- Deepak -->
    - **Property 9: Per-unit price formula correctness** — `st.floats(min_value=0.01)` for price and quantity; assert `result == price / quantity` within tolerance
    - **Property 10: Per-unit timeline excludes incomplete years** — `st.lists(st.builds(YearlyData))` with optional fields; assert no year with missing price or quantity appears in output
    - **Property 11: Per-unit inflation percentage formula** — `st.lists(st.floats(min_value=0.01), min_size=2)`; assert `(last - first) / first * 100`
    - **Validates: Requirements 5.1, 5.3, 5.5**

  - [x] 4.3 Implement deception gap calculation in `app/calculations/deception_gap.py`
    - Write `compute_deception_gap(per_unit_inflation_pct, cpi_pct) -> DeceptionGapResult` applying the color threshold rules (green 0–10, yellow 11–25, red >25)
    - Write `get_cpi_series_for_category(category: str) -> str` using the BLS series mapping table; fall back to `CUUR0000SAF` when no category match
    - _Requirements: 6.1, 6.2, 6.3, 6.5_

  - [ ]* 4.4 Write property tests for deception gap (P12, P13) <!-- Deepak -->
    - **Property 12: Deception gap formula correctness** — `st.floats()` for per-unit inflation and CPI; assert `gap == per_unit_inflation_pct - cpi_pct`
    - **Property 13: Deception gap color threshold classification** — `st.floats(min_value=0)`; assert green/yellow/red boundaries are exact
    - **Validates: Requirements 6.2, 6.3**

  - [x] 4.5 Implement cumulative quantity reduction in `app/calculations/per_unit.py`
    - Write `compute_cumulative_reduction_pct(quantity_events: list) -> float` using `(first - last) / first * 100`
    - _Requirements: 3.4_

  - [ ]* 4.6 Write property test for cumulative reduction formula (P6) <!-- Deepak -->
    - **Property 6: Cumulative quantity reduction formula** — `st.lists(st.floats(min_value=0.1), min_size=2)`; assert formula matches
    - **Validates: Requirements 3.4**

- [x] 5. Backend: BLS API client and receipt service <!-- Deepak -->
  - [x] 5.1 Implement BLS API client in `app/services/bls_client.py`
    - Write `fetch_bls_series(series_id: str, start_year: int, end_year: int) -> list[dict]` calling BLS Public Data API v2; persist results to `BLSCache` table with `fetched_at` and `bls_vintage_date`
    - On cache hit (same series_id, fetched within 24 hours), return cached data without calling BLS
    - On BLS API failure, return cached data if available; raise `BLSUnavailableError` if no cache exists
    - _Requirements: 4.2, 6.1, 12.3_

  - [x] 5.2 Implement receipt service in `app/services/receipt_service.py`
    - Write `build_receipt(product_id: str, db, bls_client) -> ShrinkflationReceipt` that assembles quantity timeline, price timeline (BLS preferred, seed fallback), per-unit timeline, deception gap, cumulative reduction, and source citations
    - Attach `data_last_updated` (now) and `staleness_warning` when `off_last_updated` is > 180 days ago
    - _Requirements: 3.1, 3.2, 4.1, 4.2, 5.2, 6.1, 7.1, 12.1, 12.2_

  - [x] 5.3 Implement receipt router in `app/routers/receipt.py`
    - Wire `GET /api/v1/receipt/{product_id}` to `receipt_service.build_receipt`; return 404 when product not found; return 503 with fallback notice when BLS is unavailable and no cache exists
    - _Requirements: 3.1, 4.1, 6.6, 12.1_

- [x] 6. Backend: Product search endpoints <!-- Deepak -->
  - [x] 6.1 Implement Open Food Facts client in `app/services/off_client.py`
    - Write `search_by_name(query: str) -> list[dict]` and `search_by_upc(upc: str) -> dict | None` calling the OFF API v2; cache responses in-memory with a 1-hour TTL
    - On OFF API failure, raise `OFFUnavailableError`
    - _Requirements: 1.2, 1.5, 2.2_

  - [x] 6.2 Implement search service in `app/services/search_service.py`
    - Write `search_products(query: str, db, off_client) -> list[ProductSearchResult]` merging seed DB results with OFF results; deduplicate by UPC; mark each result as "verified" or "unverified"
    - Write `search_by_upc(upc: str, db, off_client) -> ProductSearchResult | None`
    - On `OFFUnavailableError`, serve seed-only results and set `off_unavailable=True` in the response
    - _Requirements: 1.2, 1.4, 1.5, 2.2_

  - [x] 6.3 Implement search router in `app/routers/search.py`
    - Wire `GET /api/v1/search?q={name}` and `GET /api/v1/search?upc={code}` to the search service
    - Validate name length (1–200 chars) and UPC format (8–14 digits, numeric only); return HTTP 422 with structured error body on validation failure
    - _Requirements: 1.1, 1.3, 2.1, 2.5_

  - [ ]* 6.4 Write property tests for input validation (P1, P3) <!-- Deepak -->
    - **Property 1: Input validation rejects out-of-range queries** — `st.text()` with lengths 0, 1, 200, 201+; assert accept/reject boundary
    - **Property 3: UPC validation rejects invalid inputs** — `st.text()` with non-numeric chars, lengths < 8 and > 14; assert all rejected
    - **Validates: Requirements 1.1, 2.1, 2.5**

- [ ] 7. Checkpoint — one working end-to-end Shrinkflation Receipt <!-- Deepak -->
  - Start the FastAPI server (`uvicorn app.main:app --reload`) and verify that `GET /api/v1/receipt/{seed_product_id}` returns a full receipt JSON with quantity timeline, price timeline, per-unit timeline, deception gap, and source citations for at least one seed product.
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Frontend: Shrinkflation Receipt rendering <!-- Vijay -->
  - [ ] 8.1 Implement `SearchBar` component (`src/components/SearchBar/`)
    - Render a text input (name search) and a numeric input (UPC search) with inline validation: reject empty submit, reject name > 200 chars, reject UPC with non-numeric chars or length outside 8–14
    - On submit, call `GET /api/v1/search?q=` or `GET /api/v1/search?upc=` via `client.ts`; navigate directly to receipt page when UPC returns a single match
    - _Requirements: 1.1, 1.3, 2.1, 2.3, 2.4, 2.5_

  - [ ] 8.2 Implement `SearchResults` component (`src/components/SearchResults/`)
    - Render a list of `ProductSearchResult` items, each showing product name, brand, current net quantity with unit, and a "Verified" or "Unverified" badge
    - Show "No results found — be the first to report this product" with a link to the report form when the list is empty
    - Show an OFF-unavailable banner when `off_unavailable` is true in the response
    - _Requirements: 1.3, 1.4, 1.5_

  - [ ] 8.3 Implement `QuantityTimeline` chart (`src/components/ShrinkflationReceipt/QuantityTimeline.tsx`)
    - Render a Recharts step/line chart with net weight/volume on Y-axis and year on X-axis; mark each shrinkflation event with a distinct dot
    - Render a custom tooltip showing exact quantity, year, and source citation on hover
    - Display cumulative reduction percentage beneath the chart (e.g., "−18% since 2010")
    - Show "Quantity history unverified — contribute data" when `quantity_timeline` is empty
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ] 8.4 Implement `PriceTimeline` chart (`src/components/ShrinkflationReceipt/PriceTimeline.tsx`)
    - Render a Recharts line chart with USD price on Y-axis and year on X-axis; overlay the per-unit price line from `per_unit_timeline`
    - Render a custom tooltip showing price, year, and source citation (BLS series ID or seed entry ID) on hover
    - Display "Price data from curated seed database — not BLS" label when source is seed; display "Price history unavailable — contribute data" when `price_timeline` is empty
    - Display BLS data vintage date on the chart when source is BLS
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.2, 12.3_

  - [ ] 8.5 Implement `DeceptionGapBadge` component (`src/components/ShrinkflationReceipt/DeceptionGapBadge.tsx`)
    - Render the deception gap score with color-coded background (green/yellow/red) and the CPI series ID + date range as a visible citation
    - Show "Deception Gap: insufficient data" when `deception_gap` is null
    - Show CPI fallback label when `is_fallback_cpi` is true
    - _Requirements: 6.3, 6.4, 6.5, 6.6_

  - [ ] 8.6 Implement `SourceCitation` component (`src/components/ShrinkflationReceipt/SourceCitation.tsx`)
    - Render per-data-point citations: OFF product URL, BLS series ID + bls.gov URL, or "Seed Database — {entry_id}" with original source URL
    - Show "Unverified — contribute data" when source is unverified
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ] 8.7 Assemble `ShrinkflationReceipt` page
    - Compose QuantityTimeline, PriceTimeline, DeceptionGapBadge, and SourceCitation into a single receipt page; display `data_last_updated` timestamp and staleness warning when present
    - Wire `useReceipt` hook to `GET /api/v1/receipt/{product_id}`
    - _Requirements: 5.3, 5.4, 12.1, 12.2_

- [ ] 9. Checkpoint — demo-ready: search → receipt end-to-end in browser <!-- Vijay -->
  - Verify in the browser that a user can type a product name, see search results with verified badges, click a result, and see the full Shrinkflation Receipt with all charts, deception gap badge, and source citations rendered correctly for at least one seed product.
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Backend: Brand Leaderboard <!-- Aneesh -->
  - [x] 10.1 Implement severity score calculation in `app/calculations/severity_score.py`
    - Write `compute_severity_score(events: list[ShrinkflationEvent]) -> float` applying recency weighting (2× for events within last 3 years) and normalizing to 0–100
    - _Requirements: 8.2_

  - [ ]* 10.2 Write property tests for severity score (P17) <!-- Aneesh -->
    - **Property 17: Severity score formula correctness** — `st.lists(st.builds(ShrinkflationEvent), min_size=1)`; assert recency_weight=2.0 for recent events, 1.0 otherwise, and normalized result in [0, 100]
    - **Validates: Requirements 8.2**

  - [x] 10.3 Implement leaderboard service in `app/services/leaderboard_service.py`
    - Write `get_leaderboard(db) -> list[BrandLeaderboardEntry]` returning brands sorted by severity_score descending, each with brand name, affected product count, average deception gap, severity score, last-updated timestamp, and total verified event count
    - Write `get_brand_detail(brand_id: str, db) -> BrandDetail` returning only verified events for that brand with links to product receipts
    - _Requirements: 8.1, 8.3, 8.4, 8.6_

  - [x] 10.4 Implement leaderboard router in `app/routers/leaderboard.py`
    - Wire `GET /api/v1/leaderboard` and `GET /api/v1/leaderboard/{brand_id}` to the leaderboard service; return 404 when brand not found
    - _Requirements: 8.1, 8.4_

- [ ] 11. Frontend: Brand Leaderboard <!-- Vijay -->
  - Implement `BrandLeaderboard` component (`src/components/BrandLeaderboard/`) rendering a ranked table with brand name, affected products, average deception gap, and severity score; clicking a row navigates to a brand detail view showing all verified events with links to individual receipts
  - Display last-updated timestamp and total verified event count below the table
  - Wire `useLeaderboard` hook to `GET /api/v1/leaderboard` and `GET /api/v1/leaderboard/{brand_id}`
  - _Requirements: 8.1, 8.3, 8.4, 8.6_

- [ ]* 11.1 Write property tests for leaderboard invariants (P16, P18, P19) <!-- Aneesh -->
  - **Property 16: Leaderboard descending sort invariant** — `st.lists(st.builds(BrandEntry), min_size=2)`; assert `brands[i].severity_score >= brands[i+1].severity_score` for all adjacent pairs
  - **Property 18: Leaderboard entry required fields** — `st.builds(BrandEntry)`; assert non-null brand name, affected products, avg deception gap, severity score
  - **Property 19: Brand detail contains only verified events for that brand** — `st.lists(st.builds(ShrinkflationEvent))`; assert all events have `verification_status == "verified"` and matching `brand_id`
  - **Validates: Requirements 8.1, 8.3, 8.4**

- [x] 12. Backend: Crowdsourced Reporting <!-- Aneesh -->
  - [x] 12.1 Implement report service in `app/services/report_service.py`
    - Write `submit_report(submission: ReportSubmission, db) -> CrowdsourcedReport` that validates required fields (product name, brand, before-quantity, after-quantity, date), persists the report with `verification_status="unverified"` and a UUID `submission_id`, and returns the stored record
    - Write `auto_verify_report(report_id: str, db, off_client) -> CrowdsourcedReport` that cross-checks the report against OFF data; if matched, set `verification_status="verified"` and populate `confirming_source`
    - _Requirements: 9.2, 9.3, 9.4, 9.5_

  - [x] 12.2 Implement report router in `app/routers/reports.py`
    - Wire `POST /api/v1/reports` to accept multipart form data (report fields + optional image); validate image as JPEG or PNG and ≤ 5 MB; return HTTP 422 with structured error on validation failure; return confirmation with `submission_id` on success
    - _Requirements: 9.1, 9.2, 9.3, 9.6_

  - [ ]* 12.3 Write property tests for report submission (P20, P21, P22, P23, P24) <!-- Aneesh -->
    - **Property 20: Report validation rejects incomplete reports** — `st.builds(ReportSubmission)` with nulled required fields; assert API returns 422 and does not persist
    - **Property 21: Submission IDs are unique** — `st.lists(st.builds(ReportSubmission), min_size=2)`; assert all `submission_id` values are distinct
    - **Property 22: New reports start as unverified** — `st.builds(ReportSubmission)`; assert `verification_status == "unverified"` on creation
    - **Property 23: Auto-verification sets status and cites source** — `st.builds(ReportSubmission)` with matching mock OFF data; assert `verification_status == "verified"` and `confirming_source` is non-null after auto-verify
    - **Property 24: Image upload validation rejects invalid files** — `st.binary()` with sizes > 5 MB and non-JPEG/PNG MIME types; assert rejection with inline error
    - **Validates: Requirements 9.2, 9.3, 9.4, 9.5, 9.6**

- [ ] 13. Frontend: Crowdsourced Report Form <!-- Vijay -->
  - Implement `ReportForm` component (`src/components/ReportForm/`) with fields: product name, UPC (optional), brand, before-quantity + unit, after-quantity + unit, date (month/year), price at change (optional), image upload (JPEG/PNG, max 5 MB)
  - Validate required fields client-side before submit; validate image size and type client-side with inline error messages; pre-fill UPC when navigated from a "Product not found" UPC search
  - On successful submission, display confirmation message with the returned `submission_id`
  - _Requirements: 9.1, 9.2, 9.3, 9.6_

- [x] 14. Backend: Grocery List Calculator <!-- Aneesh -->
  - [x] 14.1 Implement calculator service in `app/services/calculator_service.py`
    - Write `calculate_grocery_list(request: GroceryListRequest, db, bls_client) -> GroceryListResponse` that for each item: validates `weekly_quantity` in [1, 52], retrieves current and 2019-baseline per-unit prices, computes `annual_hidden_cost = (current_per_unit - baseline_per_unit) * weekly_quantity * 52`, and sums all item costs into `total_annual_hidden_cost`
    - Return `has_data=False` with "No shrinkflation data available" for items with no verified data
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [x] 14.2 Implement CSV/PDF export in `app/services/calculator_service.py`
    - Write `export_csv(results: GroceryListResponse) -> str` generating a CSV with columns: product name, weekly quantity, baseline per-unit price, current per-unit price, annual hidden cost, source citations
    - Write `export_pdf(results: GroceryListResponse) -> bytes` generating a PDF with the same data using a lightweight library (e.g., reportlab or fpdf2)
    - _Requirements: 10.6_

  - [x] 14.3 Implement calculator router in `app/routers/calculator.py`
    - Wire `POST /api/v1/calculator` to the calculator service; add `GET /api/v1/calculator/export?format=csv|pdf` for export
    - _Requirements: 10.1, 10.6_

  - [ ]* 14.4 Write property tests for calculator (P25, P26, P27, P28) <!-- Aneesh -->
    - **Property 25: Grocery list weekly quantity validation** — `st.integers()` outside [1, 52]; assert calculator returns validation error
    - **Property 26: Annual hidden cost formula correctness** — `st.floats(min_value=0.01)` for prices, `st.integers(1, 52)` for quantity; assert `(current - baseline) * qty * 52`
    - **Property 27: Total grocery list cost is sum of item costs** — `st.lists(st.builds(GroceryItemResult), min_size=1)`; assert `total == sum(item.annual_hidden_cost)`
    - **Property 28: CSV export contains source citations for all items** — `st.lists(st.builds(GroceryItemResult), min_size=1)`; assert N rows each with non-empty citation columns
    - **Validates: Requirements 10.1, 10.3, 10.4, 10.6**

- [ ] 15. Frontend: Grocery List Calculator <!-- Vijay -->
  - Implement `GroceryCalculator` component (`src/components/GroceryCalculator/`) with an add-product interface (name or UPC search), weekly quantity input (1–52), per-item deception gap and annual hidden cost display, total annual hidden cost summary, and export buttons (PDF and CSV)
  - Show "No shrinkflation data available" for items with `has_data=false`
  - Display the calculation methodology formula beneath the total
  - Wire `useGroceryList` hook to `POST /api/v1/calculator`
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [ ] 16. Data Sources page and remaining backend routes <!-- Vijay + Aneesh -->
  - Implement `DataSourcesPage` component (`src/components/DataSourcesPage/`) listing Open Food Facts, BLS, and the seed database with update frequencies and terms-of-use links
  - Implement `GET /api/v1/sources` router in `app/routers/sources.py` returning the data sources list
  - _Requirements: 12.4_

- [x] 17. Remaining property-based tests <!-- Aneesh -->
  - [ ]* 17.1 Write property tests for search result fields (P2, P4) <!-- Aneesh -->
    - **Property 2: Search results contain all required display fields** — `st.builds(ProductSearchResult)`; assert non-null name, brand, quantity, unit, and verification_status in {"verified","unverified"}
    - **Property 4: UPC exact-match invariant** — `st.from_regex(r'\d{8,14}')`; assert returned product UPC equals submitted UPC
    - **Validates: Requirements 1.4, 2.2**

  - [ ]* 17.2 Write property tests for receipt data (P5, P7, P8, P14, P15, P30) <!-- Aneesh -->
    - **Property 5: Quantity timeline data completeness** — `st.lists(st.builds(ShrinkflationEvent), min_size=1)`; assert exactly N event data points each with non-null quantity, year, and source citation
    - **Property 7: Price data source priority** — `st.booleans()` for BLS availability; assert `source_type=="bls"` when BLS data exists, `"seed"` otherwise
    - **Property 8: Tooltip completeness for timeline data points** — `st.builds(QuantityDataPoint | PriceDataPoint)`; assert tooltip payload has value, year, and non-empty source identifier
    - **Property 14: Deception gap citation completeness** — `st.builds(DeceptionGapResult)`; assert non-null `cpi_series_id` and `cpi_date_range` tuple
    - **Property 15: Source citation format by source type** — `st.sampled_from(["bls","open_food_facts","seed"])` + data; assert URL/ID patterns match spec
    - **Property 30: Receipt data freshness metadata** — `st.datetimes()` for `off_last_updated`; assert non-null `data_last_updated`, staleness warning when > 180 days, non-null `bls_vintage_date` for BLS points
    - **Validates: Requirements 3.1, 3.2, 3.3, 4.2, 4.3, 7.1, 7.2, 7.3, 7.4, 12.1, 12.2, 12.3**

  - [ ]* 17.3 Write property test for seed database entry completeness (P29) <!-- Aneesh -->
    - **Property 29: Seed database entry completeness** — iterate over all entries in `seed_data.json`; assert each has non-null product name, UPC, brand, ≥ 2 quantity data points with dates, ≥ 1 price data point, and ≥ 1 source citation per data point
    - **Validates: Requirements 11.2**

- [ ] 18. Frontend component tests (Vitest + React Testing Library) <!-- Vijay -->
  - [ ]* 18.1 Write snapshot and unit tests for `DeceptionGapBadge` <!-- Vijay -->
    - Snapshot tests for green (gap=5), yellow (gap=15), and red (gap=30) color rendering
    - Test "Deception Gap: insufficient data" renders when `deception_gap` is null
    - Test CPI fallback label renders when `is_fallback_cpi` is true
    - _Requirements: 6.3, 6.5, 6.6_

  - [ ]* 18.2 Write snapshot tests for `SourceCitation` <!-- Vijay -->
    - Snapshot tests for OFF, BLS, and seed citation formats
    - Test "Unverified — contribute data" renders for unverified source
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ]* 18.3 Write unit tests for `SearchBar` validation <!-- Vijay -->
    - Test empty submit is blocked; test 201-character name is rejected with inline error; test non-numeric UPC is rejected; test UPC < 8 digits is rejected
    - _Requirements: 1.1, 2.1, 2.5_

  - [ ]* 18.4 Write unit tests for `ReportForm` validation <!-- Vijay -->
    - Test required-field validation blocks submission; test image > 5 MB is rejected client-side with inline error; test non-JPEG/PNG file is rejected
    - _Requirements: 9.2, 9.6_

- [ ] 19. Integration tests <!-- Aneesh -->
  - [ ]* 19.1 Write BLS cache integration test <!-- Aneesh -->
    - Fetch a BLS series once; mock the BLS HTTP endpoint; assert the second call returns cached data without hitting the network
    - _Requirements: 4.2_

  - [ ]* 19.2 Write OFF fallback integration test <!-- Aneesh -->
    - Mock OFF to return 503; call `GET /api/v1/search?q=chips`; assert response contains seed-only results and the fallback notice banner
    - _Requirements: 1.5_

  - [ ]* 19.3 Write auto-verification pipeline integration test <!-- Aneesh -->
    - Submit a crowdsourced report matching a seed product; run auto-verify; assert `verification_status == "verified"` and `confirming_source` is non-null
    - _Requirements: 9.5_

  - [ ]* 19.4 Write leaderboard refresh integration test <!-- Aneesh -->
    - Verify a crowdsourced report; assert the affected brand's severity score is recalculated in the leaderboard response
    - _Requirements: 8.5_

- [ ] 20. Smoke tests and startup assertions <!-- Deepak -->
  - Add startup assertions in `app/main.py` (or a `tests/test_smoke.py` run at startup): assert `len(events) >= 20`, `len(distinct_brands) >= 10`, `len(distinct_categories) >= 5` after seed load
  - Assert all BLS category-to-series mappings in `bls_client.py` resolve to known series IDs
  - _Requirements: 11.1, 11.3_

- [ ] 21. Final checkpoint — all features working, all tests passing <!-- Deepak + Aneesh + Vijay -->
  - Run `pytest tests/ --hypothesis-seed=0` and `vitest --run`; fix any failures
  - Verify the full user journey in the browser: search → receipt → leaderboard → report form → grocery calculator → export
  - Ensure all tests pass, ask the user if questions arise.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP demo
- The sequencing prioritizes a working end-to-end demo (Tasks 1–9) before layering on additional features
- Each task references specific requirements for traceability
- All 30 correctness properties from the design document are covered by property-based tests using Hypothesis
- Property tests are placed close to their corresponding implementation tasks to catch errors early
- Checkpoints at Tasks 3, 7, 9, and 21 ensure incremental validation throughout development
