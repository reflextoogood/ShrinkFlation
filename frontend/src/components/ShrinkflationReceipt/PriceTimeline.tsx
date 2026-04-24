import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import type { PriceDataPoint, PerUnitDataPoint } from '../../types'

interface Props {
  priceData: PriceDataPoint[]
  perUnitData: PerUnitDataPoint[]
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.[0]) return null
  const d = payload[0].payload
  return (
    <div className="chart-tooltip">
      {d.price_usd != null && <p style={{ margin: 0, color: '#10B981' }}>Price: ${d.price_usd.toFixed(2)}</p>}
      {d.per_unit_price != null && <p style={{ margin: 0, color: '#22D3EE' }}>Per-unit: ${d.per_unit_price.toFixed(3)}</p>}
      <p style={{ margin: 0, color: '#94A3B8' }}>{d.year}</p>
      {d.citation && <p style={{ margin: 0, color: '#64748B', fontSize: '0.75rem' }}>{d.bls_series_id ?? d.citation.label}</p>}
    </div>
  )
}

export default function PriceTimeline({ priceData, perUnitData }: Props) {
  if (priceData.length === 0) {
    return <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Price history unavailable — <a href="/report">contribute data</a></p>
  }

  const isSeed = priceData[0]?.source_type === 'seed'
  const blsVintage = priceData[0]?.citation?.bls_vintage_date

  const merged = priceData.map(p => {
    const pu = perUnitData.find(u => u.year === p.year)
    return { ...p, per_unit_price: pu?.per_unit_price ?? null }
  })

  return (
    <div className="glass">
      <h3 style={{ margin: '0 0 0.25rem', fontSize: '0.9rem', color: 'var(--text-dim)' }}>Price Timeline</h3>
      {isSeed && <p style={{ fontSize: '0.75rem', color: 'var(--coral)', margin: '0 0 0.5rem' }}>⚠ Price data from curated seed database — not BLS</p>}
      {blsVintage && <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0 0 0.5rem' }}>BLS vintage: {blsVintage}</p>}
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={merged} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
          <XAxis dataKey="year" stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 12 }} />
          <YAxis tickFormatter={v => `$${v}`} stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ color: '#94A3B8', fontSize: '0.8rem' }} />
          <Line type="monotone" dataKey="price_usd" name="Price (USD)" stroke="#10B981" strokeWidth={2} dot={{ r: 3, fill: '#10B981' }} />
          <Line type="monotone" dataKey="per_unit_price" name="Per-unit price" stroke="#22D3EE" strokeWidth={2} dot={{ r: 3, fill: '#22D3EE' }} connectNulls />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
