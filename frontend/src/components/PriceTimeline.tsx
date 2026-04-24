import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts'
import type { PriceDataPoint, PerUnitDataPoint } from '../types'
import { Card } from './ui/Card'

interface Props {
  priceData: PriceDataPoint[]
  perUnitData: PerUnitDataPoint[]
}

export function PriceTimeline({ priceData, perUnitData }: Props) {
  if (priceData.length === 0) {
    return (
      <Card>
        <p className="text-slate-400 text-sm text-center py-8">
          Price history unavailable — <a href="/report" className="text-blue-400 hover:underline">contribute data</a>
        </p>
      </Card>
    )
  }

  const perUnitByYear = Object.fromEntries(perUnitData.map(p => [p.year, p.per_unit_price]))
  const chartData = priceData.map(d => ({
    year: d.year,
    price: d.price_usd,
    perUnit: perUnitByYear[d.year],
    source: d.source_type,
    citation: d.citation.label,
  }))

  const isSeed = priceData[0]?.source_type === 'seed'

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-slate-200">Price Over Time</h3>
        {isSeed && (
          <span className="text-xs text-slate-500 bg-slate-700 px-2 py-0.5 rounded">
            Seed Database — not BLS
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="year" stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} />
          <YAxis stroke="#94a3b8" tick={{ fill: '#94a3b8', fontSize: 12 }} tickFormatter={v => `$${v}`} />
          <Tooltip
            contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, color: '#f1f5f9' }}
            formatter={(val: number, name: string) => [`$${val.toFixed(2)}`, name === 'price' ? 'Price' : 'Per-unit']}
          />
          <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
          <Line type="monotone" dataKey="price" name="Price" stroke="#3b82f6" strokeWidth={2}
            dot={{ fill: '#1e293b', stroke: '#3b82f6', strokeWidth: 2, r: 4 }}
            isAnimationActive animationDuration={600} />
          <Line type="monotone" dataKey="perUnit" name="Per-unit" stroke="#a78bfa" strokeWidth={2}
            strokeDasharray="4 2"
            dot={{ fill: '#1e293b', stroke: '#a78bfa', strokeWidth: 2, r: 3 }}
            isAnimationActive animationDuration={700} />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  )
}
