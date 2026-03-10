import { useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

import Home from './pages/Home'
import CreditDashboard from './pages/CreditDashboard'
import PortfolioDashboard from './pages/PortfolioDashboard'
import brandMark from './assets/intelli-credit-mark.svg'

const VIEWS = [
  { id: 'underwrite', label: 'Underwriting Studio', icon: '🤖' },
  { id: 'credit', label: 'Credit Dashboard', icon: '📊' },
  { id: 'portfolio', label: 'Portfolio Monitor', icon: '📈' },
]

export default function App() {
  const [activeView, setActiveView] = useState('underwrite')

  const ActivePage = useMemo(() => {
    if (activeView === 'credit') return CreditDashboard
    if (activeView === 'portfolio') return PortfolioDashboard
    return Home
  }, [activeView])

  return (
    <div className="app-shell">
      <div className="ambient-shape ambient-shape-blue" />
      <div className="ambient-shape ambient-shape-purple" />
      <div className="ambient-shape ambient-shape-teal" />

      <header className="sticky top-0 z-30 border-b border-white/20 bg-white/45 backdrop-blur-xl">
        <div className="mx-auto flex w-full max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <img src={brandMark} alt="Intelli-Credit" className="h-10 w-auto" />
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sky-700">Intelli-Credit</p>
              <h1 className="text-lg font-bold text-slate-900 sm:text-xl">AI Corporate Credit Decision Engine</h1>
            </div>
          </div>

          <nav className="flex flex-wrap items-center gap-2 rounded-2xl border border-slate-200/80 bg-white/80 p-1 shadow-sm">
            {VIEWS.map((view) => {
              const isActive = view.id === activeView
              return (
                <button
                  key={view.id}
                  type="button"
                  onClick={() => setActiveView(view.id)}
                  className={`rounded-xl px-3 py-2 text-sm font-semibold transition sm:px-4 ${
                    isActive
                      ? 'bg-gradient-to-r from-blue-600 via-purple-600 to-emerald-500 text-white shadow-lg shadow-blue-500/30'
                      : 'text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <span className="mr-1.5">{view.icon}</span>
                  {view.label}
                </button>
              )
            })}
          </nav>
        </div>
      </header>

      <AnimatePresence mode="wait">
        <motion.div
          key={activeView}
          className="page-enter"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.24, ease: 'easeInOut' }}
        >
          <ActivePage />
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
