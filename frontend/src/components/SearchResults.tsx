import { useNavigate } from 'react-router-dom'
import type { ProductSearchResult } from '../types'
import { VerifiedBadge } from './ui/Badge'
import { Card } from './ui/Card'

interface Props {
  results: ProductSearchResult[]
  offUnavailable: boolean
}

export function SearchResults({ results, offUnavailable }: Props) {
  const navigate = useNavigate()

  return (
    <div className="space-y-4 animate-fade-in">
      {offUnavailable && (
        <div className="bg-yellow-900/30 border border-yellow-700 text-yellow-300 rounded-lg px-4 py-3 text-sm">
          ⚠ Open Food Facts is currently unavailable — showing verified seed data only.
        </div>
      )}

      {results.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <div className="text-5xl mb-4">🔍</div>
          <p className="text-lg font-medium text-slate-300">No results found</p>
          <p className="text-sm mt-1">Be the first to report this product</p>
          <button
            onClick={() => navigate('/report')}
            className="mt-4 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-5 py-2.5 rounded-lg transition-colors duration-150"
          >
            + Report a product
          </button>
        </div>
      ) : (
        results.map(r => (
          <Card
            key={r.id}
            className="cursor-pointer hover:border-slate-500 hover:shadow-md transition-all duration-200"
          >
            <button
              className="w-full text-left"
              onClick={() => navigate(`/receipt/${r.id}`)}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="font-semibold text-slate-100 text-base">{r.name}</h3>
                  <p className="text-slate-400 text-sm mt-0.5">{r.brand}</p>
                  {r.current_quantity && (
                    <p className="text-slate-500 text-xs mt-1">
                      Current: {r.current_quantity} {r.quantity_unit}
                    </p>
                  )}
                </div>
                <VerifiedBadge status={r.verification_status} />
              </div>
            </button>
          </Card>
        ))
      )}
    </div>
  )
}
