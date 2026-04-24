import type { SourceCitation as Citation } from '../../types'

function CitationItem({ c }: { c: Citation }) {
  if (c.source_type === 'unverified') {
    return <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>Unverified — <a href="/report">contribute data</a></span>
  }
  if (c.source_type === 'open_food_facts') {
    return <a href={c.source_url} target="_blank" rel="noopener noreferrer">{c.label}</a>
  }
  if (c.source_type === 'bls') {
    const url = c.source_url ?? `https://data.bls.gov/timeseries/${c.source_id}`
    return (
      <span>
        BLS: <a href={url} target="_blank" rel="noopener noreferrer">{c.source_id}</a>
        {c.bls_vintage_date && <span style={{ color: 'var(--text-muted)', fontSize: '0.8em' }}> (vintage {c.bls_vintage_date})</span>}
      </span>
    )
  }
  return (
    <span>
      Seed Database — {c.source_id}
      {c.source_url && <> (<a href={c.source_url} target="_blank" rel="noopener noreferrer">source</a>)</>}
    </span>
  )
}

export default function SourceCitation({ sources }: { sources: Citation[] }) {
  if (sources.length === 0) return null
  return (
    <div className="glass">
      <h3 style={{ margin: '0 0 0.5rem', fontSize: '0.9rem', color: 'var(--text-dim)' }}>Sources</h3>
      <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--text-dim)' }}>
        {sources.map((c, i) => (
          <li key={i} style={{ marginBottom: '0.25rem' }}><CitationItem c={c} /></li>
        ))}
      </ul>
    </div>
  )
}
