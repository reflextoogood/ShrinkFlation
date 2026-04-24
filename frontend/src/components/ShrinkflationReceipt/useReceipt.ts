import { useState, useEffect } from 'react'
import { api, APIError } from '../../api/client'
import type { ShrinkflationReceipt } from '../../types'

export function useReceipt(productId: string | undefined) {
  const [receipt, setReceipt] = useState<ShrinkflationReceipt | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!productId) return
    setLoading(true)
    setError('')
    api.get<ShrinkflationReceipt>(`/receipt/${productId}`)
      .then(setReceipt)
      .catch(e => setError(e instanceof APIError && e.status === 404 ? 'Product not found' : 'Failed to load receipt'))
      .finally(() => setLoading(false))
  }, [productId])

  return { receipt, loading, error }
}
