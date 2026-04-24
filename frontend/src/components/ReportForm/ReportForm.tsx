import { useState, type FormEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../../api/client'

interface ReportResponse { submission_id: string }

const UNITS = ['oz', 'g', 'ml', 'fl oz', 'lb', 'kg', 'ct']

export default function ReportForm() {
  const [params] = useSearchParams()
  const [form, setForm] = useState({
    product_name: '', upc: params.get('upc') ?? '', brand: '',
    before_quantity: '', before_unit: 'oz', after_quantity: '', after_unit: 'oz',
    date_month: '', date_year: '', price_at_change: '',
  })
  const [image, setImage] = useState<File | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [submissionId, setSubmissionId] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const set = (k: string, v: string) => { setForm(f => ({ ...f, [k]: v })); setErrors(e => ({ ...e, [k]: '' })) }

  const validate = () => {
    const e: Record<string, string> = {}
    if (!form.product_name.trim()) e.product_name = 'Required'
    if (!form.brand.trim()) e.brand = 'Required'
    if (!form.before_quantity || +form.before_quantity <= 0) e.before_quantity = 'Must be > 0'
    if (!form.after_quantity || +form.after_quantity <= 0) e.after_quantity = 'Must be > 0'
    if (!form.date_month || +form.date_month < 1 || +form.date_month > 12) e.date_month = '1–12'
    if (!form.date_year || +form.date_year < 1990 || +form.date_year > new Date().getFullYear()) e.date_year = 'Invalid year'
    if (image) {
      if (!['image/jpeg', 'image/png'].includes(image.type)) e.image = 'JPEG or PNG only'
      if (image.size > 5 * 1024 * 1024) e.image = 'Max 5 MB'
    }
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setSubmitting(true)
    try {
      const fd = new FormData()
      Object.entries(form).forEach(([k, v]) => v && fd.append(k, v))
      if (image) fd.append('image', image)
      const res = await api.postForm<ReportResponse>('/reports', fd)
      setSubmissionId(res.submission_id)
    } catch {
      setErrors({ _form: 'Submission failed. Please try again.' })
    } finally {
      setSubmitting(false)
    }
  }

  if (submissionId) {
    return (
      <div className="glass fade-up" style={{ textAlign: 'center', padding: '2.5rem' }}>
        <h2 style={{ color: 'var(--emerald)' }}>✓ Report Submitted</h2>
        <p style={{ color: 'var(--text-dim)' }}>Submission ID: <code style={{ color: 'var(--cyan)' }}>{submissionId}</code></p>
      </div>
    )
  }

  const labelStyle = { display: 'block', fontSize: '0.8rem', fontWeight: 500 as const, color: 'var(--text-dim)', marginBottom: '0.25rem' }

  return (
    <div className="fade-up">
      <h2>Report Shrinkflation</h2>
      <form onSubmit={submit} className="glass" style={{ display: 'grid', gap: '0.75rem', maxWidth: '520px', marginTop: '1rem' }}>
        <div>
          <label style={labelStyle}>Product Name *</label>
          <input className="input" value={form.product_name} onChange={e => set('product_name', e.target.value)} />
          {errors.product_name && <p className="error">{errors.product_name}</p>}
        </div>
        <div>
          <label style={labelStyle}>UPC (optional)</label>
          <input className="input" value={form.upc} onChange={e => set('upc', e.target.value)} />
        </div>
        <div>
          <label style={labelStyle}>Brand *</label>
          <input className="input" value={form.brand} onChange={e => set('brand', e.target.value)} />
          {errors.brand && <p className="error">{errors.brand}</p>}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '0.5rem' }}>
          <div>
            <label style={labelStyle}>Before Quantity *</label>
            <input type="number" step="any" className="input" value={form.before_quantity} onChange={e => set('before_quantity', e.target.value)} />
            {errors.before_quantity && <p className="error">{errors.before_quantity}</p>}
          </div>
          <div>
            <label style={labelStyle}>Unit</label>
            <select className="input" value={form.before_unit} onChange={e => set('before_unit', e.target.value)}>
              {UNITS.map(u => <option key={u}>{u}</option>)}
            </select>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '0.5rem' }}>
          <div>
            <label style={labelStyle}>After Quantity *</label>
            <input type="number" step="any" className="input" value={form.after_quantity} onChange={e => set('after_quantity', e.target.value)} />
            {errors.after_quantity && <p className="error">{errors.after_quantity}</p>}
          </div>
          <div>
            <label style={labelStyle}>Unit</label>
            <select className="input" value={form.after_unit} onChange={e => set('after_unit', e.target.value)}>
              {UNITS.map(u => <option key={u}>{u}</option>)}
            </select>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
          <div>
            <label style={labelStyle}>Month *</label>
            <input type="number" min={1} max={12} className="input" value={form.date_month} onChange={e => set('date_month', e.target.value)} />
            {errors.date_month && <p className="error">{errors.date_month}</p>}
          </div>
          <div>
            <label style={labelStyle}>Year *</label>
            <input type="number" className="input" value={form.date_year} onChange={e => set('date_year', e.target.value)} />
            {errors.date_year && <p className="error">{errors.date_year}</p>}
          </div>
        </div>
        <div>
          <label style={labelStyle}>Price at Change (optional)</label>
          <input type="number" step="0.01" className="input" value={form.price_at_change} onChange={e => set('price_at_change', e.target.value)} />
        </div>
        <div>
          <label style={labelStyle}>Image (JPEG/PNG, max 5 MB)</label>
          <input type="file" accept="image/jpeg,image/png" style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}
            onChange={e => { setImage(e.target.files?.[0] ?? null); setErrors(er => ({ ...er, image: '' })) }} />
          {errors.image && <p className="error">{errors.image}</p>}
        </div>
        {errors._form && <p className="error">{errors._form}</p>}
        <button type="submit" disabled={submitting} className="btn btn-coral">
          {submitting ? 'Submitting…' : 'Submit Report'}
        </button>
      </form>
    </div>
  )
}
