import { useParams } from 'react-router-dom'
import { useReceipt } from './useReceipt'
import QuantityTimeline from './QuantityTimeline'
import PriceTimeline from './PriceTimeline'
import DeceptionGapBadge from './DeceptionGapBadge'
import SourceCitation from './SourceCitation'

export default function ShrinkflationReceiptPage() {
  const { productId } = useParams<{ productId: string }>()
  const { receipt, loading, error } = useReceipt(productId)

  if (loading) return <p style={{ color: 'var(--text-dim)' }}>Loading receipt…</p>
  if (error) return <p className="error">{error}</p>
  if (!receipt) return null

  const { product: p } = receipt

  return (
    <div className="fade-up">
      <h2 style={{ margin: '0 0 0.25rem' }}>{p.name}</h2>
      <p style={{ color: 'var(--text-muted)', margin: '0 0 1.5rem' }}>{p.brand}{p.upc && ` · UPC ${p.upc}`}</p>

      <DeceptionGapBadge data={receipt.deception_gap} />

      <div style={{ display: 'grid', gap: '1rem', marginTop: '1.5rem' }}>
        <QuantityTimeline data={receipt.quantity_timeline} cumulativeReductionPct={receipt.cumulative_quantity_reduction_pct} />
        <PriceTimeline priceData={receipt.price_timeline} perUnitData={receipt.per_unit_timeline} />
        <SourceCitation sources={receipt.sources} />
      </div>

      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '1.5rem' }}>
        Data last updated: {new Date(receipt.data_last_updated).toLocaleDateString()}
        {receipt.staleness_warning && <span style={{ color: 'var(--coral)' }}> — {receipt.staleness_warning}</span>}
      </p>
    </div>
  )
}
