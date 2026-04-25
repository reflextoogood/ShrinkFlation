import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

export function SearchBar() {
  const [query, setQuery] = useState('')
  const [upc, setUpc] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    if (upc) {
      if (!/^\d{8,14}$/.test(upc)) {
        setError('UPC must be 8–14 numeric digits.')
        return
      }
      navigate(`/search?upc=${upc}`)
      return
    }
    if (!query.trim()) { setError('Enter a product name or UPC.'); return }
    if (query.length > 200) { setError('Name must be 200 characters or less.'); return }
    navigate(`/search?q=${encodeURIComponent(query.trim())}`)
  }

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="text"
          placeholder="Search by product name..."
          value={query}
          onChange={e => { setQuery(e.target.value); setUpc('') }}
          className="flex-1 bg-slate-800 border border-slate-600 text-slate-100 placeholder-slate-500 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-150"
        />
        <span className="text-slate-500 self-center hidden sm:block">or</span>
        <input
          type="text"
          placeholder="UPC / Barcode"
          value={upc}
          onChange={e => { setUpc(e.target.value); setQuery('') }}
          className="w-full sm:w-40 bg-slate-800 border border-slate-600 text-slate-100 placeholder-slate-500 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-150"
        />
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-3 rounded-lg transition-colors duration-150 active:scale-95"
        >
          Search
        </button>
      </div>
      {error && <p className="mt-2 text-red-400 text-sm">{error}</p>}
    </form>
  )
}
