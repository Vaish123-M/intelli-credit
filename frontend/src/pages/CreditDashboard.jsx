import { useEffect, useState } from 'react'

import DashboardStats from '../components/dashboard/DashboardStats'
import DealsTable from '../components/dashboard/DealsTable'
import RiskChart from '../components/dashboard/RiskChart'
import CopilotChat from '../components/dashboard/CopilotChat'
import { getDashboardDeals, getDashboardSummary } from '../services/api'

export default function CreditDashboard() {
  const [summary, setSummary] = useState({
    companies_analyzed: 0,
    low_risk: 0,
    medium_risk: 0,
    high_risk: 0,
  })
  const [deals, setDeals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadDashboard = async () => {
    setError('')
    setLoading(true)
    try {
      const [nextSummary, nextDeals] = await Promise.all([getDashboardSummary(), getDashboardDeals()])
      setSummary(nextSummary || {})
      setDeals(Array.isArray(nextDeals) ? nextDeals : [])
    } catch (dashboardError) {
      setError(dashboardError.message || 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  return (
    <main className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="rounded-3xl border border-white/40 bg-gradient-to-r from-blue-700 via-purple-700 to-emerald-500 p-6 text-white shadow-2xl shadow-blue-900/20">
          <p className="text-xs uppercase tracking-[0.2em] text-blue-100">Intelli-Credit</p>
          <h1 className="mt-2 text-3xl font-black tracking-tight md:text-4xl">Credit Decision Dashboard</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-200 md:text-base">
            Centralized portfolio view of analyzed companies, risk segments, and lending decisions.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <article className="glass-card gradient-outline feature-lift rounded-2xl p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">📉 Avg Risk Score</p>
            <p className="mt-2 text-2xl font-black text-slate-900">0.42</p>
            <p className="text-xs text-amber-700">Medium Risk ⚠</p>
          </article>
          <article className="glass-card gradient-outline feature-lift rounded-2xl p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">✅ Recommendation</p>
            <p className="mt-2 text-2xl font-black text-slate-900">Review Required</p>
            <p className="text-xs text-purple-700">Policy + AI blended</p>
          </article>
          <article className="glass-card gradient-outline feature-lift rounded-2xl p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">💰 Avg Interest</p>
            <p className="mt-2 text-2xl font-black text-slate-900">11.8%</p>
            <p className="text-xs text-slate-600">Risk-adjusted pricing</p>
          </article>
          <article className="glass-card gradient-outline feature-lift rounded-2xl p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">🏷 Risk Category</p>
            <p className="mt-2 text-2xl font-black text-slate-900">Dynamic</p>
            <p className="text-xs text-emerald-700">Green/Yellow/Red coding</p>
          </article>
        </section>

        <div className="flex justify-end">
          <button
            type="button"
            onClick={loadDashboard}
            disabled={loading}
            className="rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-2 text-sm font-semibold text-white shadow-md transition hover:scale-[1.03] disabled:cursor-not-allowed disabled:opacity-70"
          >
            {loading ? 'Refreshing...' : 'Refresh Dashboard'}
          </button>
        </div>

        {error && <p className="rounded-lg bg-rose-100 px-4 py-2 text-sm text-rose-700">{error}</p>}

        <DashboardStats summary={summary} />

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-1">
            <RiskChart summary={summary} />
          </div>
          <div className="lg:col-span-2">
            <DealsTable deals={deals} />
          </div>
        </div>

        <CopilotChat deals={deals} />
      </div>
    </main>
  )
}
