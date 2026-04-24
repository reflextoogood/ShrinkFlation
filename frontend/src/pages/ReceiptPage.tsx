import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'
import type { ShrinkflationReceipt } from '../types'
import { DeceptionGapBadge } from '../components/DeceptionGapBadge'
import { QuantityTimeline } from '../components/QuantityTimeline'
import { PriceTimeline } from '../components/PriceTimeline'
import { VerifiedBadge } from '../components/ui/Badge'
import { Card, Skeleton } from '../components/ui/Card'

export function ReceiptPage() {
  const { id } = useParams<{ id: string }>()
  const [receipt, setReceipt] = useState<ShrinkflationReceipt | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    api.get<ShrinkflationReceipt>(`/receipt/${id}`)
      .then(setReceipt)
      .catch(() => setError('Product not found.'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-4">
      <Skeleton className="h-10 w-64" />
      <Skeleton className="h-32 w-full" />
      <Skeleton className="h-56 w-full" />
      <Skeleton className="h-56 w-full" />
    </div>
  )

  if (error || !receipt) return (
    <div className="max-w-3xl mx-auto px-4 py-10 text-center text-slate-400">
      <div className="text-5xl mb-4">😕</div>
      <p>{error || 'Something went wrong.'}</p>
      <Link to="/" className="mt-4 inline-block text-blue-400 hover:underline">← Back to search</Link>
    </div>
  )

  const { product } = receipt

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <Link to="/" className="text-slate-400 hover:text-slate-200 text-sm transition-colors">← Back</Link>
        <div className="flex items-start justify-between mt-3 gap-4 flex-wrap">
          <div>
            <h1 className="text-2xl font-bold text-slate-100">{product.name}</h1>
            <p className="text-slate-400 mt-0.5">{product.brand} {product.upc && <span className="text-slate-500 text-xs ml-2">UPC: {product.upc}</span>}</p>
          </div>
          <VerifiedBadge status={product.verification_status as 'verified' | 'unverified'} />
        </div>
      </div>

      {/* Staleness warning */}
      {receipt.staleness_warning && (
        <div className="bg-yellow-900/30 border border-yellow-700 text-yellow-300 rounded-lg px-4 py-3 text-sm">
          ⚠ {receipt.staleness_warning}
        </div>
      )}

      {/* Deception Gap */}
      <DeceptionGapBadge gap={receipt.deception_gap} />

      {/* Quantity Timeline */}
      <QuantityTimeline
        data={receipt.quantity_timeline}
        cumulativeReduction={receipt.cumulative_quantity_reduction_pct ?? undefined}
      />

      {/* Price Timeline */}
      <PriceTimeline
        priceData={receipt.price_timeline}
        perUnitData={receipt.per_unit_timeline}
      />

      {/* Sources */}
      {receipt.sources.length > 0 && (
        <Card>
          <h3 className="font-semibold text-slate-200 mb-3">Sources</h3>
          <ul className="space-y-1.5">
            {receipt.sources.slice(0, 6).map((s, i) => (
              <li key={i} className="text-sm text-slate-400 flex items-center gap-2">
                <span className="text-slate-600">•</span>
                {s.source_url ? (
                  <a href={s.source_url} target="_blank" rel="noopener noreferrer"
                    className="text-blue-400 hover:underline truncate">{s.label}</a>
                ) : (
                  <span>{s.label}</span>
                )}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Footer */}
      <p className="text-xs text-slate-600 text-center">
        Updated: {new Date(receipt.data_last_updated).toLocaleDateString()}
      </p>
    </div>
  )
}
