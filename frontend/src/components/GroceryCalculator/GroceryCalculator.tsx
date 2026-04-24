import { useState } from 'react'
import { api } from '../../api/client'
import type { SearchResponse, GroceryListResponse, GroceryItem, GroceryItemResult, ProductSearchResult } from '../../types'

export default function GroceryCalculator() {
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState<ProductSearchResult[]>([])
  const [items, setItems] = useState<GroceryItem[]>([])
  const [itemNames, setItemNames] = useState<Record<string, string>>({})
  const [result, setResult] = useState<GroceryListResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const search = async () => {
    if (!query.trim()) return
    try {
      const data = await api.get<SearchResponse>(`/search?q=${encodeURIComponent(query)}`)
      setSearchResults(data.results)
    } catch { setSearchResults([]) }
  }

  const addProduct = (p: ProductSearchResult) => {
    if (items.some(i => i.product_id === p.id)) return
    setItems(prev => [...prev, { product_id: p.id, weekly_quantity: 1 }])
    setItemNames(prev => ({ ...prev, [p.id]: p.name }))
    setSearchResults([])
    setQuery('')
  }

  const updateQty = (id: string, qty: number) => {
    setItems(prev => prev.map(i => i.product_id === id ? { ...i, weekly_quantity: Math.max(1, Math.min(52, qty)) } : i))
  }

  const removeItem = (id: string) => setItems(prev => prev.filter(i => i.product_id !== id))

  const calculate = async () => {
    if (items.length === 0) return
    setLoading(true)
    setError('')
    try {
      setResult(await api.post<GroceryListResponse>('/calculator', { items }))
    } catch { setError('Calculation failed') }
    finally { setLoading(false) }
  }

  const exportFile = (format: 'csv' | 'pdf') => {
    window.open(`/api/v1/calculator/export?format=${format}`, '_blank')
  }

  return (
    <div className="fade-up">
      <h2>Grocery Calculator</h2>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Add products to see your annual hidden shrinkflation cost.</p>

      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem', marginBottom: '1rem' }}>
        <input className="input" placeholder="Search product…" value={query}
          onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === 'Enter' && search()}
          style={{ flex: 1 }} />
        <button onClick={search} className="btn btn-cyan" style={{ padding: '0.6rem 1rem' }}>Search</button>
      </div>

      {searchResults.length > 0 && (
        <div className="glass" style={{ marginBottom: '1rem', maxHeight: '160px', overflow: 'auto', padding: '0.5rem' }}>
          {searchResults.map(p => (
            <div key={p.id} onClick={() => addProduct(p)} style={{ padding: '0.4rem 0.5rem', cursor: 'pointer', borderRadius: '6px', transition: 'background 0.15s', color: 'var(--text)' }}
              onMouseEnter={e => (e.currentTarget.style.background = 'rgba(34,211,238,0.08)')}
              onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}>
              {p.name} <span style={{ color: 'var(--text-muted)' }}>— {p.brand}</span>
            </div>
          ))}
        </div>
      )}

      {items.length > 0 && (
        <div className="glass" style={{ marginBottom: '1rem' }}>
          <table className="table">
            <thead>
              <tr><th>Product</th><th style={{ width: '100px' }}>Weekly Qty</th><th style={{ width: '40px' }}></th></tr>
            </thead>
            <tbody>
              {items.map(i => (
                <tr key={i.product_id}>
                  <td>{itemNames[i.product_id]}</td>
                  <td>
                    <input type="number" min={1} max={52} value={i.weekly_quantity} onChange={e => updateQty(i.product_id, +e.target.value)}
                      className="input" style={{ width: '65px', padding: '0.25rem 0.4rem' }} />
                  </td>
                  <td><button onClick={() => removeItem(i.product_id)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--coral)', fontSize: '1rem' }}>✕</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {items.length > 0 && (
        <button onClick={calculate} disabled={loading} className="btn btn-coral" style={{ marginBottom: '1rem' }}>
          {loading ? 'Calculating…' : 'Calculate Hidden Cost'}
        </button>
      )}

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="glass fade-up" style={{ marginTop: '1rem' }}>
          <table className="table">
            <thead>
              <tr><th>Product</th><th>Gap</th><th style={{ textAlign: 'right' }}>Annual Hidden Cost</th></tr>
            </thead>
            <tbody>
              {result.items.map((r: GroceryItemResult) => (
                <tr key={r.product_id}>
                  <td>{r.product_name}</td>
                  <td style={{ color: 'var(--coral)' }}>
                    {r.has_data ? (r.deception_gap ? `${r.deception_gap.gap_pp.toFixed(1)} pp` : '—') : <em style={{ color: 'var(--text-muted)' }}>{r.no_data_message}</em>}
                  </td>
                  <td style={{ textAlign: 'right', color: 'var(--cyan)', fontWeight: 600 }}>
                    {r.has_data && r.annual_hidden_cost != null ? `$${r.annual_hidden_cost.toFixed(2)}` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'rgba(251,113,133,0.08)', borderRadius: '8px', textAlign: 'center' }}>
            <p style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0 }}>Total Annual Hidden Cost: <span style={{ color: 'var(--coral)' }}>${result.total_annual_hidden_cost.toFixed(2)}</span></p>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>{result.methodology}</p>
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
            <button onClick={() => exportFile('csv')} className="btn btn-ghost" style={{ padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}>Export CSV</button>
            <button onClick={() => exportFile('pdf')} className="btn btn-ghost" style={{ padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}>Export PDF</button>
          </div>
        </div>
      )}
    </div>
  )
}
