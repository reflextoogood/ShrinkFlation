import { Routes, Route } from 'react-router-dom'
import { NavBar } from './components/NavBar'
import { HomePage } from './pages/HomePage'
import { SearchPage } from './pages/SearchPage'
import { ReceiptPage } from './pages/ReceiptPage'
import { LeaderboardPage } from './pages/LeaderboardPage'
import { ReportPage } from './pages/ReportPage'

function App() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <NavBar />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/receipt/:id" element={<ReceiptPage />} />
          <Route path="/leaderboard" element={<LeaderboardPage />} />
          <Route path="/leaderboard/:id" element={<LeaderboardPage />} />
          <Route path="/report" element={<ReportPage />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
