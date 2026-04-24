import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../api/client'
import type { LeaderboardResponse, BrandDetail, BrandLeaderboardEntry } from '../../types'

function useLeaderboard() {
  const [data, setData] = useState<LeaderboardResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get<LeaderboardResponse>('/leaderboard')
      .then(setData)
      .catch(() => setError('Failed to load leaderboard'))
      .finally(() => setLoading(false))
  }, [])

  return { data, loading, error }
}

function BrandDetailView({ brandId, onBack }: { brandId: string; onBack: () => void }) {
  const [detail, setDetail] = useState<BrandDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<BrandDetail>(`/leaderboard/${brandId}`)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setLoading(false))
  }, [brandId])

  if (loading) return <p style={{ color: 'var(--text-dim)' }}>Loading…</p>
  if (!detail) return <p className="error">Brand not found</p>

  return (
    <div className="fade-up">
      <button onClick={onBack} className="btn btn-ghost" style={{ marginBottom: '1rem', padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}>← Back</button>
      <h2>{detail.name}</h2>
      <p style={{ color: 'var(--text-dim)' }}>Severity Score: <span style={{ color: 'var(--coral)', fontWeight: 700 }}>{detail.severity_score.toFixed(1)}</span></p>
      <div className="glass" style={{ marginTop: '1rem' }}>
        <table className="table">
          <thead>
            <tr><th>Product</th><th>Date</th><th>Change</th></tr>
          </thead>
          <tbody>
            {detail.events.map((e, i) => (
              <tr key={i}>
                <td><Link to={`/receipt/${e.product_id}`}>{e.product_name}</Link></td>
                <td style={{ color: 'var(--text-dim)' }}>{e.event_date}</td>
                <td><span style={{ color: 'var(--coral)' }}>{e.quantity_before} → {e.quantity_after}</span> {e.quantity_unit}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function Row({ brand, rank, onClick }: { brand: BrandLeaderboardEntry; rank: number; onClick: () => void }) {
  return (
    <tr onClick={onClick} style={{ cursor: 'pointer' }}>
      <td style={{ color: 'var(--text-muted)' }}>{rank}</td>
      <td style={{ fontWeight: 600 }}>{brand.name}</td>
      <td style={{ textAlign: 'center' }}>{brand.affected_products}</td>
      <td style={{ textAlign: 'center', color: 'var(--coral)' }}>{brand.avg_deception_gap != null ? `${brand.avg_deception_gap.toFixed(1)} pp` : '—'}</td>
      <td style={{ textAlign: 'center', color: 'var(--cyan)', fontWeight: 600 }}>{brand.severity_score.toFixed(1)}</td>
    </tr>
  )
}

export default function BrandLeaderboard() {
  const { data, loading, error } = useLeaderboard()
  const [selectedBrand, setSelectedBrand] = useState<string | null>(null)

  if (loading) return <p style={{ color: 'var(--text-dim)' }}>Loading leaderboard…</p>
  if (error) return <p className="error">{error}</p>
  if (!data) return null

  if (selectedBrand) return <BrandDetailView brandId={selectedBrand} onBack={() => setSelectedBrand(null)} />

  return (
    <div className="fade-up">
      <h2>Brand Leaderboard</h2>
      <div className="glass" style={{ marginTop: '1rem' }}>
        <table className="table">
          <thead>
            <tr>
              <th style={{ width: '40px' }}>#</th>
              <th>Brand</th>
              <th style={{ textAlign: 'center' }}>Products</th>
              <th style={{ textAlign: 'center' }}>Avg Gap</th>
              <th style={{ textAlign: 'center' }}>Severity</th>
            </tr>
          </thead>
          <tbody>
            {data.brands.map((b, i) => <Row key={b.id} brand={b} rank={i + 1} onClick={() => setSelectedBrand(b.id)} />)}
          </tbody>
        </table>
      </div>
      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
        Last updated: {new Date(data.last_updated).toLocaleDateString()} · {data.total_verified_events} verified events
      </p>
    </div>
  )
}
