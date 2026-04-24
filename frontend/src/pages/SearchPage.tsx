import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import type { SearchResponse } from '../types'
import { SearchBar } from '../components/SearchBar'
import { SearchResults } from '../components/SearchResults'
import { Skeleton } from '../components/ui/Card'

export function SearchPage() {
  const [params] = useSearchParams()
  const q = params.get('q') ?? ''
  const upc = params.get('upc') ?? ''

  const [data, setData] = useState<SearchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!q && !upc) return
    setLoading(true)
    setError('')
    const path = upc ? `/search?upc=${upc}` : `/search?q=${encodeURIComponent(q)}`
    api.get<SearchResponse>(path)
      .then(setData)
      .catch(() => setError('Search failed. Please try again.'))
      .finally(() => setLoading(false))
  }, [q, upc])

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 animate-fade-in">
      <div className="mb-8">
        <SearchBar />
      </div>

      {loading && (
        <div className="space-y-4">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-20 w-full" />)}
        </div>
      )}

      {error && <p className="text-red-400 text-sm">{error}</p>}

      {data && !loading && (
        <>
          <p className="text-slate-400 text-sm mb-4">
            {data.total} result{data.total !== 1 ? 's' : ''} for "{q || upc}"
          </p>
          <SearchResults results={data.results} offUnavailable={data.off_unavailable} />
        </>
      )}
    </div>
  )
}
