# Requirements Document

## Introduction

ShrinkFlation is a web application that exposes the practice of shrinkflation — companies reducing product quantity or weight while maintaining or increasing prices, effectively hiding inflation from consumers. The app allows users to search for grocery products by name or UPC barcode and receive a visual "Shrinkflation Receipt" documenting historical quantity changes, price trajectories, true per-unit inflation, and a "deception gap" score comparing brand behavior against official CPI data.

The application targets the Kiro Spark Challenge hackathon (Economics track — Transparency Guardrail), which requires exposing a hidden economic factor and turning invisible data into actionable financial insight. Every claim must trace to a verifiable data source; unverifiable claims must be clearly labeled.

The tech stack is: React frontend with Recharts, Python/FastAPI backend, Open Food Facts API for product data, BLS Average Price Data for historical pricing, and a seed database of 20–30 pre-researched shrinkflation examples.

---

## Glossary

- **ShrinkFlation_App**: The full web application described in this document.
- **Product**: A grocery item identified by a name and/or UPC barcode.
- **Shrinkflation_Event**: A documented instance where a product's net weight, volume, or count decreased while its retail price remained the same or increased.
- **Shrinkflation_Receipt**: The visual report generated for a product showing quantity timeline, price timeline, per-unit inflation, and deception gap score.
- **Deception_Gap**: The difference (in percentage points) between a product's true per-unit price inflation and the official CPI for the same period.
- **Per_Unit_Price**: The retail price of a product divided by its net weight, volume, or count at a given point in time.
- **CPI**: The Consumer Price Index published by the U.S. Bureau of Labor Statistics (BLS), used as the official inflation benchmark.
- **BLS_Data**: Historical average retail price data published by the U.S. Bureau of Labor Statistics.
- **Open_Food_Facts**: The open-source food product database (https://world.openfoodfacts.org) used as the primary source for product metadata and historical packaging data.
- **Seed_Database**: A curated, pre-researched dataset of 20–30 verified shrinkflation examples bundled with the application.
- **Brand_Leaderboard**: A ranked list of brands ordered by shrinkflation severity score.
- **Severity_Score**: A numeric score (0–100) assigned to a brand based on frequency, magnitude, and recency of shrinkflation events.
- **Crowdsourced_Report**: A user-submitted shrinkflation finding that includes product identification, before/after quantity, date, and optional photographic evidence.
- **Grocery_List**: A user-defined list of products and weekly purchase quantities used to calculate the hidden cost of shrinkflation on personal shopping habits.
- **Verified**: A data point that can be traced to at least one of: Open Food Facts, BLS data, or the Seed_Database.
- **Unverified**: A data point that cannot be confirmed against a recognized source; must be labeled "unverified — contribute data".
- **UPC**: Universal Product Code; a 12-digit barcode used to uniquely identify retail products.
- **API**: Application Programming Interface.

---

## Requirements

### Requirement 1: Product Search by Name

**User Story:** As a consumer, I want to search for a grocery product by name, so that I can quickly find shrinkflation data without needing to scan a barcode.

#### Acceptance Criteria

1. THE ShrinkFlation_App SHALL provide a text input field that accepts product name queries of 1–200 characters.
2. WHEN a user submits a product name query, THE ShrinkFlation_App SHALL return a list of matching products from the Seed_Database and Open_Food_Facts within 3 seconds.
3. WHEN no matching products are found, THE ShrinkFlation_App SHALL display the message "No results found — be the first to report this product" with a link to the crowdsourced reporting form.
4. WHEN search results are returned, THE ShrinkFlation_App SHALL display each result with its product name, brand, current net weight/volume, and a verified/unverified badge.
5. IF the Open_Food_Facts API is unavailable, THEN THE ShrinkFlation_App SHALL serve results exclusively from the Seed_Database and display a notice that live product data is temporarily unavailable.

---

### Requirement 2: Product Search by UPC Barcode

**User Story:** As a consumer, I want to search for a product by scanning or entering its UPC barcode, so that I can identify the exact product variant and retrieve precise shrinkflation data.

#### Acceptance Criteria

1. THE ShrinkFlation_App SHALL provide a numeric input field that accepts UPC barcodes of 8–14 digits.
2. WHEN a valid UPC is submitted, THE ShrinkFlation_App SHALL query Open_Food_Facts and the Seed_Database for an exact barcode match and return results within 3 seconds.
3. WHEN a UPC matches exactly one product, THE ShrinkFlation_App SHALL navigate directly to that product's Shrinkflation_Receipt.
4. WHEN a UPC matches no product, THE ShrinkFlation_App SHALL display the message "Product not found — contribute data" with a pre-filled crowdsourced reporting form using the submitted UPC.
5. IF the submitted UPC contains non-numeric characters or fewer than 8 digits, THEN THE ShrinkFlation_App SHALL display an inline validation error before submitting the query.

---

### Requirement 3: Shrinkflation Receipt — Quantity Timeline

**User Story:** As a consumer, I want to see a visual timeline of a product's net weight or volume changes over time, so that I can understand when and how much the product was shrunk.

#### Acceptance Criteria

1. WHEN a product with at least one Shrinkflation_Event is selected, THE ShrinkFlation_App SHALL render a line or step chart showing net weight/volume on the Y-axis and calendar year on the X-axis.
2. THE ShrinkFlation_App SHALL mark each Shrinkflation_Event on the quantity timeline with a distinct visual indicator (e.g., a labeled data point).
3. WHEN a user hovers over a data point on the quantity timeline, THE ShrinkFlation_App SHALL display a tooltip showing the exact quantity, the date of change, and the data source citation.
4. THE ShrinkFlation_App SHALL display the total cumulative quantity reduction as a percentage beneath the quantity timeline (e.g., "−18% since 2010").
5. WHEN a product has no verified quantity history, THE ShrinkFlation_App SHALL display the label "Quantity history unverified — contribute data" in place of the chart.

---

### Requirement 4: Shrinkflation Receipt — Price Timeline

**User Story:** As a consumer, I want to see a visual timeline of a product's retail price over time, so that I can see whether prices rose, held steady, or fell as quantities shrank.

#### Acceptance Criteria

1. WHEN a product is selected, THE ShrinkFlation_App SHALL render a line chart showing average retail price (USD) on the Y-axis and calendar year on the X-axis.
2. THE ShrinkFlation_App SHALL source price data from BLS_Data where available, falling back to Seed_Database values, and SHALL display the source label on the chart.
3. WHEN a user hovers over a data point on the price timeline, THE ShrinkFlation_App SHALL display a tooltip showing the price, the year, and the data source citation including the BLS series ID or Seed_Database entry ID.
4. WHEN price data is sourced from the Seed_Database rather than BLS_Data, THE ShrinkFlation_App SHALL display the label "Price data from curated seed database — not BLS" adjacent to the chart.
5. WHEN no price data is available for a product, THE ShrinkFlation_App SHALL display the label "Price history unavailable — contribute data" in place of the chart.

---

### Requirement 5: Shrinkflation Receipt — Per-Unit Inflation Calculation

**User Story:** As a consumer, I want to see the true per-unit price inflation for a product, so that I can understand the real cost increase beyond what the sticker price suggests.

#### Acceptance Criteria

1. WHEN both quantity history and price history are available for a product, THE ShrinkFlation_App SHALL calculate Per_Unit_Price for each year as: retail price divided by net weight/volume.
2. THE ShrinkFlation_App SHALL display the Per_Unit_Price trend as a line chart overlaid with or adjacent to the nominal price chart.
3. THE ShrinkFlation_App SHALL display the total Per_Unit_Price inflation percentage from the earliest to the most recent data point (e.g., "Per-unit cost up 47% since 2012").
4. WHEN displaying Per_Unit_Price calculations, THE ShrinkFlation_App SHALL show the formula used (price ÷ quantity = per-unit cost) and cite the underlying data sources.
5. IF quantity or price data is partially missing for a year, THEN THE ShrinkFlation_App SHALL exclude that year from the Per_Unit_Price calculation and display a note indicating the gap.

---

### Requirement 6: Shrinkflation Receipt — Deception Gap Score

**User Story:** As a consumer, I want to see a "deception gap" score that compares a product's true per-unit inflation to official CPI, so that I can understand how much worse the real cost increase is compared to what the government reports.

#### Acceptance Criteria

1. WHEN Per_Unit_Price inflation is calculable for a product, THE ShrinkFlation_App SHALL retrieve the relevant BLS CPI series for the product's food category for the same date range.
2. THE ShrinkFlation_App SHALL calculate the Deception_Gap as: Per_Unit_Price inflation percentage minus CPI percentage for the same period.
3. THE ShrinkFlation_App SHALL display the Deception_Gap as a numeric score with a color-coded label: green (0–10 pp above CPI), yellow (11–25 pp above CPI), red (>25 pp above CPI).
4. THE ShrinkFlation_App SHALL display the CPI series ID and date range used in the Deception_Gap calculation as a visible citation.
5. WHEN CPI data for the relevant food category is unavailable, THE ShrinkFlation_App SHALL use the overall Food CPI series (BLS series CUUR0000SAF) as a fallback and label it accordingly.
6. IF Per_Unit_Price inflation cannot be calculated, THEN THE ShrinkFlation_App SHALL display "Deception Gap: insufficient data" rather than a numeric score.

---

### Requirement 7: Data Source Attribution

**User Story:** As a researcher or journalist, I want every data point in the app to cite its source, so that I can verify claims independently and trust the information presented.

#### Acceptance Criteria

1. THE ShrinkFlation_App SHALL display a source citation for every data point shown in the Shrinkflation_Receipt, including the source name, URL or series ID, and retrieval date.
2. WHEN a data point originates from Open_Food_Facts, THE ShrinkFlation_App SHALL display the Open Food Facts product URL as the citation.
3. WHEN a data point originates from BLS_Data, THE ShrinkFlation_App SHALL display the BLS series ID and the BLS data portal URL as the citation.
4. WHEN a data point originates from the Seed_Database, THE ShrinkFlation_App SHALL display "Seed Database — [entry ID]" and the original source used to compile that entry (e.g., news article URL, manufacturer press release URL).
5. WHEN a data point cannot be traced to a verified source, THE ShrinkFlation_App SHALL display the label "Unverified — contribute data" instead of presenting the value as fact.

---

### Requirement 8: Brand Leaderboard

**User Story:** As a consumer advocate, I want to see which brands practice shrinkflation most aggressively, so that I can make informed purchasing decisions and hold companies accountable.

#### Acceptance Criteria

1. THE ShrinkFlation_App SHALL display a Brand_Leaderboard ranking brands by Severity_Score in descending order.
2. THE ShrinkFlation_App SHALL calculate Severity_Score for each brand using: number of verified Shrinkflation_Events, average quantity reduction per event (%), and recency weighting (events within the last 3 years weighted 2×).
3. THE ShrinkFlation_App SHALL display each brand's entry on the leaderboard with: brand name, number of affected products, average Deception_Gap, and Severity_Score.
4. WHEN a user clicks a brand on the leaderboard, THE ShrinkFlation_App SHALL display a filtered list of all verified Shrinkflation_Events for that brand with links to individual product Shrinkflation_Receipts.
5. THE ShrinkFlation_App SHALL update the Brand_Leaderboard to reflect newly verified Crowdsourced_Reports within 24 hours of verification.
6. THE ShrinkFlation_App SHALL display the leaderboard's last-updated timestamp and the total number of verified events used to compute rankings.

---

### Requirement 9: Crowdsourced Reporting

**User Story:** As a consumer, I want to submit a shrinkflation finding I discovered, so that I can contribute to the community database and help others avoid hidden price increases.

#### Acceptance Criteria

1. THE ShrinkFlation_App SHALL provide a submission form that collects: product name, UPC (optional), brand, before-quantity with unit, after-quantity with unit, date of change (month and year), retail price at time of change (optional), and an optional image upload (JPEG or PNG, max 5 MB).
2. WHEN a user submits a Crowdsourced_Report, THE ShrinkFlation_App SHALL validate that product name, brand, before-quantity, after-quantity, and date fields are non-empty before accepting the submission.
3. WHEN a Crowdsourced_Report is successfully submitted, THE ShrinkFlation_App SHALL display a confirmation message and assign the report a unique submission ID.
4. THE ShrinkFlation_App SHALL label all Crowdsourced_Reports as "Unverified — community submission" until a moderator or automated cross-check against Open_Food_Facts or BLS_Data confirms the data.
5. WHEN a Crowdsourced_Report is cross-checked against Open_Food_Facts or BLS_Data and the data matches, THE ShrinkFlation_App SHALL automatically update the report's status to "Verified" and cite the confirming source.
6. IF a submitted image file exceeds 5 MB or is not JPEG or PNG, THEN THE ShrinkFlation_App SHALL display an inline error message and reject the upload without submitting the form.

---

### Requirement 10: Weekly Grocery List Calculator

**User Story:** As a household shopper, I want to enter my weekly grocery items and see the total hidden cost of shrinkflation on my shopping habits, so that I can understand the real financial impact on my budget.

#### Acceptance Criteria

1. THE ShrinkFlation_App SHALL provide a Grocery_List interface where users can add products by name or UPC and specify a weekly purchase quantity (1–52 units per item).
2. WHEN a product is added to the Grocery_List, THE ShrinkFlation_App SHALL display the product's current Deception_Gap and estimated annual hidden cost per unit based on Per_Unit_Price inflation since the earliest available data point.
3. THE ShrinkFlation_App SHALL calculate and display the total estimated annual hidden cost of shrinkflation across all items in the Grocery_List.
4. THE ShrinkFlation_App SHALL display the calculation methodology: (current Per_Unit_Price − baseline Per_Unit_Price) × annual purchase quantity = annual hidden cost per item.
5. WHEN a product in the Grocery_List has no verified shrinkflation data, THE ShrinkFlation_App SHALL display "No shrinkflation data available" for that item rather than estimating a cost.
6. THE ShrinkFlation_App SHALL allow users to export the Grocery_List calculation as a PDF or CSV file, with all source citations included in the export.

---

### Requirement 11: Seed Database Coverage

**User Story:** As a first-time visitor, I want the app to have meaningful data immediately available, so that I can explore shrinkflation examples without needing to search for obscure products.

#### Acceptance Criteria

1. THE ShrinkFlation_App SHALL include a Seed_Database containing a minimum of 20 verified Shrinkflation_Events across at least 10 distinct brands at initial launch.
2. EACH entry in the Seed_Database SHALL include: product name, UPC, brand, at least two quantity data points with dates, at least one price data point, and a source citation for each data point.
3. THE ShrinkFlation_App SHALL cover at least 5 distinct grocery categories in the Seed_Database (e.g., snacks, beverages, dairy, household goods, cereals).
4. WHEN a Seed_Database entry's source citation is a URL, THE ShrinkFlation_App SHALL verify at build time that the URL is reachable and flag broken links for manual review.

---

### Requirement 12: Data Freshness and Transparency

**User Story:** As a user, I want to know how current the data is, so that I can assess whether the information reflects recent shrinkflation activity.

#### Acceptance Criteria

1. THE ShrinkFlation_App SHALL display a "Data last updated" timestamp on every Shrinkflation_Receipt, indicating when the underlying data was last fetched or verified.
2. WHEN Open_Food_Facts data for a product was last updated more than 180 days ago, THE ShrinkFlation_App SHALL display a staleness warning: "Product data may be outdated — last updated [date]".
3. THE ShrinkFlation_App SHALL display the BLS data vintage (the publication date of the price series used) on every chart that uses BLS_Data.
4. THE ShrinkFlation_App SHALL provide a public-facing data sources page listing all data sources used, their update frequencies, and links to their terms of use.
