import type { DeceptionGapResult } from '../types'
import { Card } from './ui/Card'

const colors = {
  green:  { bg: 'bg-green-900/30 border-green-700', text: 'text-green-400', icon: '🟢' },
  yellow: { bg: 'bg-yellow-900/30 border-yellow-700', text: 'text-yellow-400', icon: '🟡' },
  red:    { bg: 'bg-red-900/30 border-red-700', text: 'text-red-400', icon: '🔴' },
}

export function DeceptionGapBadge({ gap }: { gap?: DeceptionGapResult }) {
  if (!gap) {
    return (
      <Card className="text-slate-400 text-sm">
        Deception Gap: insufficient data
      </Card>
    )
  }

  const c = colors[gap.color]

  return (
    <Card className={`border ${c.bg}`}>
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wide font-medium mb-1">Deception Gap</p>
          <div className={`text-3xl font-bold tabular-nums ${c.text}`}>
            {c.icon} +{gap.gap_pp.toFixed(1)} pp
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Per-unit inflation: <span className="text-slate-200 font-medium">{gap.per_unit_inflation_pct.toFixed(1)}%</span>
            {' '}vs CPI: <span className="text-slate-200 font-medium">{gap.cpi_pct.toFixed(1)}%</span>
          </p>
        </div>
        <div className="text-right text-xs text-slate-500">
          <p>Series: {gap.cpi_series_id}</p>
          <p>{gap.cpi_date_range[0]}–{gap.cpi_date_range[1]}</p>
          {gap.is_fallback_cpi && <p className="text-yellow-500 mt-0.5">⚠ Fallback CPI used</p>}
        </div>
      </div>
    </Card>
  )
}
