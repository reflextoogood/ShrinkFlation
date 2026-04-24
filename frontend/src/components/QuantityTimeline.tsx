import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceDot,
} from 'recharts'
import type { QuantityDataPoint } from '../types'
import { Card } from './ui/Card'

interface Props {
  data: QuantityDataPoint[]
  cumulativeReduction?: number
}

export function QuantityTimeline({ data, cumulativeReduction }: Props) {
  if (data.length === 0) {
    return (
      <Card>
        <p className="text-slate-400 text-sm text-center py-8">
          Quantity history unverified — <a href="/report" className="text-blue-400 hover:underline">contribute data</a>
        </p>
      </Card>
    )
  }

  const chartData = data.map(d => ({
    year: d.year,
    quantity: d.quantity_value,
    unit: d.quantity_unit,
    isShrink: d.is_shrinkflation_event,
    citation: d.citation.label,
  }))

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-slate-200">Quantity Over Time</h3>
        {cumulativeReduction !== undefined && (
          <span className="text-red-400 font-semibold tabular-nums text-sm">
            −{cumulativeReduction.toFixed(1)}% since {data[0]?.year}
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="year" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
          <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
          <Tooltip
            contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }}
            formatter={(val: number, _: string, props: { payload?: { unit?: string; citation?: string } }) => [
              `${val} ${props.payload?.unit ?? ''}`,
              'Quantity',
            ]}
            labelFormatter={label => `Year: ${label}`}
          />
          <Line
            type="stepAfter"
            dataKey="quantity"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={(props) => {
              const { cx, cy, payload } = props
              return (
                <circle
                  key={`dot-${payload.year}`}
                  cx={cx} cy={cy} r={payload.isShrink ? 6 : 4}
                  fill={payload.isShrink ? '#ef4444' : '#1e293b'}
                  stroke={payload.isShrink ? '#ef4444' : '#f59e0b'}
                  strokeWidth={2}
                />
              )
            }}
            isAnimationActive
            animationDuration={600}
          />
        </LineChart>
      </ResponsiveContainer>
      <p className="text-xs text-slate-500 mt-2">● Red dots = shrinkflation events</p>
    </Card>
  )
}
