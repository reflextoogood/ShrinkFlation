import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import type { LeaderboardResponse } from '../types'
import { DeceptionBadge } from '../components/ui/Badge'
import { Card, Skeleton } from '../components/ui/Card'

export function LeaderboardPage() {
  const [data, setData] = useState<LeaderboardResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    api.get<LeaderboardResponse>('/leaderboard')
      .then(setData)
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-100">🏆 Worst Shrinkflation Brands</h1>
        {data && (
          <p className="text-slate-400 text-sm mt-1">
            {data.total_verified_events} verified events · Updated {new Date(data.last_updated).toLocaleDateString()}
          </p>
        )}
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1,2,3,4,5].map(i => <Skeleton key={i} className="h-16 w-full" />)}
        </div>
      ) : (
        <Card className="p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700 text-slate-400 text-xs uppercase tracking-wide">
                <th className="text-left px-6 py-3">#</th>
                <th className="text-left px-4 py-3">Brand</th>
                <th className="text-center px-4 py-3">Products</th>
                <th className="text-center px-4 py-3">Avg Gap</th>
                <th className="text-right px-6 py-3">Score</th>
              </tr>
            </thead>
            <tbody>
              {data?.brands.map((brand, i) => (
                <tr
                  key={brand.id}
                  onClick={() => navigate(`/leaderboard/${brand.id}`)}
                  className="border-b border-slate-700/50 hover:bg-slate-700/30 cursor-pointer transition-colors duration-150"
                >
                  <td className="px-6 py-4 text-slate-500 font-medium">{i + 1}</td>
                  <td className="px-4 py-4 font-semibold text-slate-100">{brand.name}</td>
                  <td className="px-4 py-4 text-center text-slate-400">{brand.affected_products}</td>
                  <td className="px-4 py-4 text-center">
                    {brand.avg_deception_gap != null ? (
                      <DeceptionBadge
                        color={brand.avg_deception_gap > 25 ? 'red' : brand.avg_deception_gap > 10 ? 'yellow' : 'green'}
                        gap={brand.avg_deception_gap}
                      />
                    ) : <span className="text-slate-600">—</span>}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <div className="w-20 bg-slate-700 rounded-full h-1.5">
                        <div
                          className="bg-blue-500 h-1.5 rounded-full transition-all duration-500"
                          style={{ width: `${brand.severity_score}%` }}
                        />
                      </div>
                      <span className="text-slate-300 tabular-nums font-medium w-8 text-right">
                        {brand.severity_score.toFixed(0)}
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  )
}
