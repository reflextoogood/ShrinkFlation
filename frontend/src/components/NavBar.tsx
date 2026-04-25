import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Search', exact: true },
  { to: '/leaderboard', label: '🏆 Leaderboard' },
  { to: '/report', label: '📝 Report' },
]

export function NavBar() {
  return (
    <nav className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur border-b border-slate-800">
      <div className="max-w-5xl mx-auto px-4 flex items-center justify-between h-14">
        <NavLink to="/" className="flex items-center gap-2 font-bold text-slate-100 hover:text-white transition-colors">
          <span className="text-xl">🧾</span>
          <span>ShrinkFlation</span>
        </NavLink>
        <div className="flex items-center gap-1">
          {links.map(({ to, label, exact }) => (
            <NavLink
              key={to}
              to={to}
              end={exact}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg text-sm font-medium transition-colors duration-150 ${
                  isActive
                    ? 'bg-slate-700 text-slate-100'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  )
}
