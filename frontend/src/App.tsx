import { Routes, Route } from 'react-router-dom'

function App() {
  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', maxWidth: '1200px', margin: '0 auto', padding: '0 1rem' }}>
      <header style={{ borderBottom: '2px solid #e53e3e', padding: '1rem 0', marginBottom: '2rem' }}>
        <h1 style={{ margin: 0, color: '#e53e3e' }}>🧾 ShrinkFlation</h1>
        <p style={{ margin: '0.25rem 0 0', color: '#666', fontSize: '0.9rem' }}>
          Exposing hidden price increases — every claim cites its source
        </p>
      </header>
      <Routes>
        <Route path="/" element={<div><h2>Search for a product to see its Shrinkflation Receipt</h2></div>} />
      </Routes>
    </div>
  )
}

export default App
