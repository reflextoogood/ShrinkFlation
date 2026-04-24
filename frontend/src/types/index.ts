export type VerificationStatus = 'verified' | 'unverified'
export type DeceptionGapColor = 'green' | 'yellow' | 'red'
export type SourceType = 'open_food_facts' | 'bls' | 'seed' | 'unverified'

export interface SourceCitation {
  source_type: SourceType
  source_id?: string
  source_url?: string
  label: string
  retrieved_at?: string
  bls_vintage_date?: string
}

export interface QuantityDataPoint {
  year: number
  month?: number
  quantity_value: number
  quantity_unit: string
  is_shrinkflation_event: boolean
  citation: SourceCitation
}

export interface PriceDataPoint {
  year: number
  month?: number
  price_usd: number
  source_type: string
  bls_series_id?: string
  citation: SourceCitation
}

export interface PerUnitDataPoint {
  year: number
  per_unit_price: number
  price_usd: number
  quantity_value: number
  quantity_unit: string
}

export interface DeceptionGapResult {
  gap_pp: number
  color: DeceptionGapColor
  per_unit_inflation_pct: number
  cpi_pct: number
  cpi_series_id: string
  cpi_date_range: [number, number]
  is_fallback_cpi: boolean
}

export interface ProductDetail {
  id: string
  name: string
  brand: string
  brand_id: string
  upc?: string
  category?: string
  verification_status: string
  off_last_updated?: string
}

export interface ShrinkflationReceipt {
  product: ProductDetail
  quantity_timeline: QuantityDataPoint[]
  price_timeline: PriceDataPoint[]
  per_unit_timeline: PerUnitDataPoint[]
  deception_gap?: DeceptionGapResult
  cumulative_quantity_reduction_pct?: number
  total_per_unit_inflation_pct?: number
  data_last_updated: string
  staleness_warning?: string
  sources: SourceCitation[]
}

export interface ProductSearchResult {
  id: string
  name: string
  brand: string
  current_quantity?: number
  quantity_unit?: string
  verification_status: VerificationStatus
  upc?: string
  category?: string
}

export interface SearchResponse {
  results: ProductSearchResult[]
  off_unavailable: boolean
  total: number
}

export interface BrandLeaderboardEntry {
  id: string
  name: string
  affected_products: number
  avg_deception_gap?: number
  severity_score: number
  event_count: number
}

export interface LeaderboardResponse {
  brands: BrandLeaderboardEntry[]
  last_updated: string
  total_verified_events: number
}

export interface GroceryItem {
  product_id: string
  weekly_quantity: number
}

export interface GroceryItemResult {
  product_id: string
  product_name: string
  weekly_quantity: number
  deception_gap?: DeceptionGapResult
  baseline_per_unit_price?: number
  current_per_unit_price?: number
  annual_hidden_cost?: number
  has_data: boolean
  no_data_message?: string
  sources: SourceCitation[]
}

export interface GroceryListResponse {
  items: GroceryItemResult[]
  total_annual_hidden_cost: number
  methodology: string
}

export interface BrandDetailEvent {
  product_id: string
  product_name: string
  event_date: string
  quantity_before: number
  quantity_after: number
  quantity_unit: string
}

export interface BrandDetail {
  id: string
  name: string
  severity_score: number
  events: BrandDetailEvent[]
}
