import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../api/client'
import type { SearchResponse } from '../../types'

export interface SearchBarProps {
  onResults?: (data: SearchResponse) => void
  onError?: (msg: string) => void
  onLoading?: (loading: boolean) => void
}

export default function SearchBar({ onResults, onError, onLoading }: SearchBarProps) {
  const [name, setName] = useState('')
  const [upc, setUpc] = useState('')
  const [nameError, setNameError] = useState('')
  const [upcError, setUpcError] = useState('')
  const navigate = useNavigate()

  const validateName = (v: string) => {
    if (v.length > 200) return 'Name must be 200 characters or fewer'
    return ''
  }

  const validateUpc = (v: string) => {
    if (v && !/^\d+$/.test(v)) return 'UPC must contain only digits'
    if (v && (v.length < 8 || v.length > 14)) return 'UPC must be 8–14 digits'
    return ''
  }

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    const trimmedName = name.trim()
    const trimmedUpc = upc.trim()

    if (!trimmedName && !trimmedUpc) {
      setNameError('Enter a product name or UPC')
      return
    }

    const nErr = trimmedName ? validateName(trimmedName) : ''
    const uErr = trimmedUpc ? validateUpc(trimmedUpc) : ''
    setNameError(nErr)
    setUpcError(uErr)
    if (nErr || uErr) return

    onLoading?.(true)
    onError?.('')
    try {
      const path = trimmedUpc
        ? `/search?upc=${encodeURIComponent(trimmedUpc)}`
        : `/search?q=${encodeURIComponent(trimmedName)}`
      const data = await api.get<SearchResponse>(path)

      if (trimmedUpc && data.results.length === 1) {
        navigate(`/receipt/${data.results[0].id}`)
        return
      }
      onResults?.(data)
    } catch {
      onError?.('Search failed. Please try again.')
    } finally {
      onLoading?.(false)
    }
  }

  return (
    <form onSubmit={submit} className="glass" style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'flex-start', padding: '1rem' }}>
      <div style={{ flex: '1 1 220px' }}>
        <input
          type="text"
          className="input"
          placeholder="Product name…"
          value={name}
          onChange={e => { setName(e.target.value); setNameError('') }}
          aria-label="Product name"
        />
        {nameError && <p role="alert" className="error">{nameError}</p>}
      </div>
      <div style={{ flex: '0 1 180px' }}>
        <input
          type="text"
          inputMode="numeric"
          className="input"
          placeholder="UPC code…"
          value={upc}
          onChange={e => { setUpc(e.target.value); setUpcError('') }}
          aria-label="UPC code"
        />
        {upcError && <p role="alert" className="error">{upcError}</p>}
      </div>
      <button type="submit" className="btn btn-cyan">Search</button>
    </form>
  )
}
