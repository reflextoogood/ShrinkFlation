import { Link } from 'react-router-dom'
import type { SearchResponse } from '../../types'

export default function SearchResults({ results, off_unavailable }: SearchResponse) {
  if (results.length === 0) {
    return (
      <div className="glass" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-dim)' }}>
        <p>No results found — <Link to="/report">be the first to report this product</Link></p>
      </div>
    )
  }

  return (
    <div>
      {off_unavailable && (
        <div role="alert" className="glass" style={{ background: 'rgba(251, 113, 133, 0.1)', borderColor: 'rgba(251, 113, 133, 0.3)', marginBottom: '1rem', padding: '0.6rem 1rem', fontSize: '0.85rem', color: 'var(--coral)' }}>
          ⚠️ Open Food Facts is currently unavailable. Showing local results only.
        </div>
      )}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {results.map(p => (
          <Link key={p.id} to={`/receipt/${p.id}`} className="glass" style={{ textDecoration: 'none', color: 'inherit', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 1rem', cursor: 'pointer' }}>
            <div>
              <strong style={{ color: 'var(--text)' }}>{p.name}</strong>
              {p.brand && <span style={{ color: 'var(--text-dim)' }}> — {p.brand}</span>}
              {p.current_quantity != null && (
                <span style={{ marginLeft: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  {p.current_quantity} {p.quantity_unit}
                </span>
              )}
            </div>
            <span className={`badge ${p.verification_status === 'verified' ? 'badge-emerald' : 'badge-coral'}`}>
              {p.verification_status === 'verified' ? '✓ Verified' : 'Unverified'}
            </span>
          </Link>
        ))}
      </div>
    </div>
  )
}
