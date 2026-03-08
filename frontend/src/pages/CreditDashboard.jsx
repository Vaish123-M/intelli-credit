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
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#dbeafe,#f8fafc_35%,#fef3c7_90%)] px-4 py-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="rounded-3xl bg-slate-900 p-6 text-white shadow-xl">
          <p className="text-xs uppercase tracking-[0.2em] text-sky-200">Intelli-Credit</p>
          <h1 className="mt-2 text-3xl font-black tracking-tight md:text-4xl">Credit Decision Dashboard</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-200 md:text-base">
            Centralized portfolio view of analyzed companies, risk segments, and lending decisions.
          </p>
        </header>

        <div className="flex justify-end">
          <button
            type="button"
            onClick={loadDashboard}
            disabled={loading}
            className="rounded-xl bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500 disabled:cursor-not-allowed disabled:bg-sky-300"
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
