import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Dot } from 'recharts'
import type { QuantityDataPoint } from '../../types'

interface Props {
  data: QuantityDataPoint[]
  cumulativeReductionPct?: number
}

function EventDot(props: any) {
  const { cx, cy, payload } = props
  if (!payload.is_shrinkflation_event) return <Dot {...props} r={3} fill="#22D3EE" />
  return <Dot cx={cx} cy={cy} r={6} fill="#FB7185" stroke="#0F172A" strokeWidth={2} />
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.[0]) return null
  const d: QuantityDataPoint = payload[0].payload
  return (
    <div className="chart-tooltip">
      <p style={{ margin: 0, fontWeight: 600, color: '#22D3EE' }}>{d.quantity_value} {d.quantity_unit}</p>
      <p style={{ margin: 0, color: '#94A3B8' }}>{d.year}</p>
      <p style={{ margin: 0, color: '#64748B', fontSize: '0.75rem' }}>{d.citation.label}</p>
    </div>
  )
}

export default function QuantityTimeline({ data, cumulativeReductionPct }: Props) {
  if (data.length === 0) {
    return <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Quantity history unverified — <a href="/report">contribute data</a></p>
  }

  return (
    <div className="glass">
      <h3 style={{ margin: '0 0 0.75rem', fontSize: '0.9rem', color: 'var(--text-dim)' }}>Quantity Timeline</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
          <XAxis dataKey="year" stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 12 }} />
          <YAxis domain={['auto', 'auto']} stroke="#64748B" tick={{ fill: '#94A3B8', fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Line type="stepAfter" dataKey="quantity_value" stroke="#22D3EE" strokeWidth={2} dot={<EventDot />} />
        </LineChart>
      </ResponsiveContainer>
      {cumulativeReductionPct != null && (
        <p className="fade-up" style={{ fontSize: '0.85rem', color: 'var(--coral)', fontWeight: 600, margin: '0.5rem 0 0' }}>
          −{cumulativeReductionPct.toFixed(1)}% since {data[0].year}
        </p>
      )}
    </div>
  )
}
