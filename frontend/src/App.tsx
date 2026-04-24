import { useState } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import SearchBar from './components/SearchBar'
import SearchResults from './components/SearchResults'
import ShrinkflationReceiptPage from './components/ShrinkflationReceipt'
import BrandLeaderboard from './components/BrandLeaderboard'
import ReportForm from './components/ReportForm'
import GroceryCalculator from './components/GroceryCalculator'
import DataSourcesPage from './components/DataSourcesPage'
import type { SearchResponse } from './types'

const NAV = [
  { to: '/', label: 'Search' },
  { to: '/leaderboard', label: 'Leaderboard' },
  { to: '/report', label: 'Report' },
  { to: '/calculator', label: 'Calculator' },
  { to: '/sources', label: 'Sources' },
]

function HomePage() {
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  return (
    <div className="fade-up">
      <h2 style={{ fontWeight: 300, fontSize: '1.5rem', marginBottom: '1.5rem' }}>
        Search for a product to see its <span style={{ color: 'var(--cyan)', fontWeight: 600 }}>Shrinkflation Receipt</span>
      </h2>
      <SearchBar onResults={setResults} onError={setError} onLoading={setLoading} />
      {loading && <p style={{ color: 'var(--text-dim)', marginTop: '1rem' }}>Searching…</p>}
      {error && <p className="error" style={{ marginTop: '1rem' }}>{error}</p>}
      {results && <div style={{ marginTop: '1.5rem' }}><SearchResults {...results} /></div>}
    </div>
  )
}

function App() {
  const location = useLocation()

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <nav style={{
        position: 'fixed', top: 0, left: 0, bottom: 0, width: '160px',
        background: 'rgba(15, 23, 42, 0.7)', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)',
        borderRight: '1px solid var(--border)',
        display: 'flex', flexDirection: 'column', paddingTop: '1.25rem', gap: '0.25rem', zIndex: 50,
      }}>
        <Link to="/" style={{ textDecoration: 'none', padding: '0 1rem', marginBottom: '1.25rem' }}>
          <span style={{ fontSize: '1.1rem', fontWeight: 700 }}>
            <span style={{ color: 'var(--coral)' }}>Shrink</span><span style={{ color: 'var(--cyan)' }}>Flation</span>
          </span>
        </Link>
        {NAV.map(n => {
          const active = n.to === '/' ? location.pathname === '/' : location.pathname.startsWith(n.to)
          return (
            <Link key={n.to} to={n.to} style={{
              textDecoration: 'none', fontSize: '0.85rem', padding: '0.5rem 1rem',
              color: active ? 'var(--cyan)' : 'var(--text-dim)',
              background: active ? 'rgba(34, 211, 238, 0.08)' : 'transparent',
              borderLeft: active ? '2px solid var(--cyan)' : '2px solid transparent',
              fontWeight: active ? 600 : 400,
              transition: 'all 0.2s',
            }}>
              {n.label}
            </Link>
          )
        })}
      </nav>

      {/* Main content */}
      <main style={{ marginLeft: '160px', flex: 1, padding: '2rem 2.5rem', maxWidth: '1200px' }}>
        <header style={{ marginBottom: '2rem' }}>
          <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.8rem', fontWeight: 300 }}>
            Exposing hidden price increases — every claim cites its source
          </p>
        </header>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/receipt/:productId" element={<ShrinkflationReceiptPage />} />
          <Route path="/leaderboard" element={<BrandLeaderboard />} />
          <Route path="/report" element={<ReportForm />} />
          <Route path="/calculator" element={<GroceryCalculator />} />
          <Route path="/sources" element={<DataSourcesPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
