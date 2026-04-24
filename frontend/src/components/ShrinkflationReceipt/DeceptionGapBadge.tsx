import type { DeceptionGapResult } from '../../types'

const BG = { green: 'rgba(16, 185, 129, 0.15)', yellow: 'rgba(250, 204, 21, 0.15)', red: 'rgba(251, 113, 133, 0.15)' } as const
const FG = { green: '#10B981', yellow: '#FACC15', red: '#FB7185' } as const
const GLOW = { green: 'rgba(16,185,129,0.3)', yellow: 'rgba(250,204,21,0.3)', red: 'rgba(251,113,133,0.3)' } as const

export default function DeceptionGapBadge({ data }: { data?: DeceptionGapResult | null }) {
  if (!data) {
    return <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Deception Gap: insufficient data</p>
  }

  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column', gap: '0.25rem' }}>
      <div className="fade-up" style={{
        background: BG[data.color], color: FG[data.color],
        border: `1px solid ${FG[data.color]}33`,
        padding: '0.6rem 1.25rem', borderRadius: '12px',
        fontWeight: 700, fontSize: '1.15rem', textAlign: 'center',
        boxShadow: `0 0 20px ${GLOW[data.color]}`,
      }}>
        Deception Gap: {data.gap_pp.toFixed(1)} pp
      </div>
      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        CPI: {data.cpi_series_id} ({data.cpi_date_range[0]}–{data.cpi_date_range[1]})
        {data.is_fallback_cpi && <em> (fallback — general food CPI)</em>}
      </span>
    </div>
  )
}
