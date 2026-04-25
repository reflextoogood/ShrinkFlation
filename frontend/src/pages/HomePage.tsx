import SearchBar from '../components/SearchBar'

export function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-16 animate-fade-in">
      <div className="text-center mb-10">
        <div className="text-6xl mb-4">🧾</div>
        <h1 className="text-4xl font-bold text-slate-100 mb-3">ShrinkFlation</h1>
        <p className="text-slate-400 text-lg max-w-md mx-auto">
          Companies are shrinking products while keeping prices the same.
          <span className="text-slate-200"> We're tracking it.</span>
        </p>
      </div>

      <SearchBar />

      <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-3xl w-full">
        {[
          { icon: '📉', label: 'Track quantity reductions over time' },
          { icon: '🔴', label: 'See the real hidden price increase' },
          { icon: '📋', label: 'Every claim cites its source' },
        ].map(({ icon, label }) => (
          <div key={label} className="bg-slate-800/50 border border-slate-700 rounded-xl p-5 text-center">
            <div className="text-3xl mb-2">{icon}</div>
            <p className="text-slate-400 text-sm">{label}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
