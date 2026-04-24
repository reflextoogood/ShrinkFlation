import { useState, type FormEvent } from 'react'
import { api } from '../api/client'
import { Card } from '../components/ui/Card'

const UNITS = ['oz', 'g', 'ml', 'lbs', 'fl oz', 'sheets', 'count']
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

export function ReportPage() {
  const [form, setForm] = useState({
    product_name: '', brand: '', upc: '',
    before_quantity: '', before_unit: 'oz',
    after_quantity: '', after_unit: 'oz',
    change_month: '1', change_year: '2023',
    price_at_change: '',
  })
  const [image, setImage] = useState<File | null>(null)
  const [imageError, setImageError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  function set(key: string, val: string) {
    setForm(f => ({ ...f, [key]: val }))
  }

  function handleImage(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    setImageError('')
    if (!file) return
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
      setImageError('Only JPEG or PNG images are allowed.')
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      setImageError('Image must be 5 MB or smaller.')
      return
    }
    setImage(file)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    if (!form.product_name || !form.brand || !form.before_quantity || !form.after_quantity) {
      setError('Please fill in all required fields.')
      return
    }
    setSubmitting(true)
    const fd = new FormData()
    Object.entries(form).forEach(([k, v]) => fd.append(k, v))
    if (image) fd.append('image', image)
    try {
      const res = await api.postForm<{ submission_id: string }>('/reports', fd)
      setSuccess(`Report submitted! ID: ${res.submission_id}`)
    } catch {
      setError('Submission failed. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (success) return (
    <div className="max-w-lg mx-auto px-4 py-16 text-center animate-fade-in">
      <div className="text-5xl mb-4">✅</div>
      <h2 className="text-xl font-bold text-slate-100 mb-2">Report Submitted!</h2>
      <p className="text-slate-400 text-sm">{success}</p>
    </div>
  )

  return (
    <div className="max-w-lg mx-auto px-4 py-10 animate-fade-in">
      <h1 className="text-2xl font-bold text-slate-100 mb-6">📝 Report Shrinkflation</h1>
      <Card>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Product Name *">
            <input className={input} value={form.product_name} onChange={e => set('product_name', e.target.value)} placeholder="e.g. Doritos Nacho Cheese" />
          </Field>
          <Field label="Brand *">
            <input className={input} value={form.brand} onChange={e => set('brand', e.target.value)} placeholder="e.g. Frito-Lay" />
          </Field>
          <Field label="UPC (optional)">
            <input className={input} value={form.upc} onChange={e => set('upc', e.target.value)} placeholder="12-digit barcode" />
          </Field>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Before Quantity *">
              <div className="flex gap-2">
                <input className={`${input} flex-1`} type="number" value={form.before_quantity} onChange={e => set('before_quantity', e.target.value)} placeholder="10.0" />
                <select className={`${input} w-20`} value={form.before_unit} onChange={e => set('before_unit', e.target.value)}>
                  {UNITS.map(u => <option key={u}>{u}</option>)}
                </select>
              </div>
            </Field>
            <Field label="After Quantity *">
              <div className="flex gap-2">
                <input className={`${input} flex-1`} type="number" value={form.after_quantity} onChange={e => set('after_quantity', e.target.value)} placeholder="8.0" />
                <select className={`${input} w-20`} value={form.after_unit} onChange={e => set('after_unit', e.target.value)}>
                  {UNITS.map(u => <option key={u}>{u}</option>)}
                </select>
              </div>
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Field label="Month *">
              <select className={input} value={form.change_month} onChange={e => set('change_month', e.target.value)}>
                {MONTHS.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
              </select>
            </Field>
            <Field label="Year *">
              <input className={input} type="number" value={form.change_year} onChange={e => set('change_year', e.target.value)} min="2000" max="2026" />
            </Field>
          </div>

          <Field label="Price at Change (optional)">
            <input className={input} type="number" step="0.01" value={form.price_at_change} onChange={e => set('price_at_change', e.target.value)} placeholder="$4.99" />
          </Field>

          <Field label="Photo (optional)">
            <input type="file" accept="image/jpeg,image/png" onChange={handleImage}
              className="text-slate-400 text-sm file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-slate-700 file:text-slate-200 file:text-sm hover:file:bg-slate-600 cursor-pointer" />
            {imageError && <p className="text-red-400 text-xs mt-1">{imageError}</p>}
          </Field>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button type="submit" disabled={submitting}
            className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition-colors duration-150 active:scale-95">
            {submitting ? 'Submitting...' : 'Submit Report'}
          </button>
        </form>
      </Card>
    </div>
  )
}

const input = "w-full bg-slate-900 border border-slate-600 text-slate-100 placeholder-slate-500 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-150 text-sm"

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-400 mb-1.5">{label}</label>
      {children}
    </div>
  )
}
