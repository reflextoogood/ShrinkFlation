import { useState, useEffect } from 'react'
import { api } from '../../api/client'

interface DataSource {
  name: string
  description: string
  url: string
  update_frequency: string
  terms_url: string
}

export default function DataSourcesPage() {
  const [sources, setSources] = useState<DataSource[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get<DataSource[]>('/sources')
      .then(setSources)
      .catch(() => setError('Failed to load data sources'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p style={{ color: 'var(--text-dim)' }}>Loading…</p>
  if (error) return <p className="error">{error}</p>

  return (
    <div className="fade-up">
      <h2>Data Sources</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>All shrinkflation claims are backed by these data sources.</p>
      <div style={{ display: 'grid', gap: '1rem', marginTop: '1rem' }}>
        {sources.map(s => (
          <div key={s.name} className="glass">
            <h3 style={{ margin: '0 0 0.25rem', fontSize: '1rem' }}>
              <a href={s.url} target="_blank" rel="noopener noreferrer">{s.name}</a>
            </h3>
            <p style={{ margin: '0 0 0.5rem', fontSize: '0.9rem', color: 'var(--text-dim)' }}>{s.description}</p>
            <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Updates: {s.update_frequency} · <a href={s.terms_url} target="_blank" rel="noopener noreferrer">Terms of Use</a>
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
