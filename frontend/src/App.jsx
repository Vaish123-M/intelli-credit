import { useState } from 'react'

import CreditDashboard from './pages/CreditDashboard'
import Home from './pages/Home'

export default function App() {
  const [activeView, setActiveView] = useState('underwriting')

  return (
    <div>
      <nav className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl gap-2 px-4 py-3">
          <button
            type="button"
            onClick={() => setActiveView('underwriting')}
            className={`rounded-full px-4 py-2 text-sm font-semibold ${
              activeView === 'underwriting' ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Underwriting Flow
          </button>
          <button
            type="button"
            onClick={() => setActiveView('dashboard')}
            className={`rounded-full px-4 py-2 text-sm font-semibold ${
              activeView === 'dashboard' ? 'bg-sky-700 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Credit Dashboard
          </button>
        </div>
      </nav>

      {activeView === 'underwriting' ? <Home /> : <CreditDashboard />}
    </div>
  )
}
