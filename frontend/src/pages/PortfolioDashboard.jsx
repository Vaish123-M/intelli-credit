import { useEffect, useState } from 'react'

import ExposureChart from '../components/portfolio/ExposureChart'
import HighRiskTable from '../components/portfolio/HighRiskTable'
import PortfolioStats from '../components/portfolio/PortfolioStats'
import { getDashboardDeals, getPortfolioAlerts, getPortfolioHighRisk } from '../services/api'

const AUTO_REFRESH_MS = 15000

function parseLoanLimit(value) {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value
  }

  const numeric = Number(String(value ?? '').replace(/[^\d.-]/g, ''))
  return Number.isFinite(numeric) ? numeric : 0
}

function buildSummaryFromCompanies(companies) {
  const records = Array.isArray(companies) ? companies : []

  const lowRiskCount = records.filter((company) => company?.risk_category === 'Low Risk').length
  const mediumRiskCount = records.filter((company) => company?.risk_category === 'Medium Risk').length
  const highRiskCount = records.filter((company) => company?.risk_category === 'High Risk').length
  const totalExposure = records.reduce((sum, company) => sum + parseLoanLimit(company?.loan_limit), 0)

  return {
    companies_analyzed: records.length,
    total_exposure: totalExposure,
    low_risk: lowRiskCount,
    medium_risk: mediumRiskCount,
    high_risk: highRiskCount,
  }
}

export default function PortfolioDashboard() {
  const [summary, setSummary] = useState({
    companies_analyzed: 0,
    total_exposure: 0,
    low_risk: 0,
    medium_risk: 0,
    high_risk: 0,
  })
  const [alerts, setAlerts] = useState([])
  const [highRiskRecords, setHighRiskRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadPortfolio = async () => {
    setLoading(true)
    setError('')
    try {
      const [analyzedCompanies, nextAlerts, nextHighRisk] = await Promise.all([
        getDashboardDeals(),
        getPortfolioAlerts(),
        getPortfolioHighRisk(),
      ])
      setSummary(buildSummaryFromCompanies(analyzedCompanies))
      setAlerts(Array.isArray(nextAlerts) ? nextAlerts : [])
      setHighRiskRecords(Array.isArray(nextHighRisk) ? nextHighRisk : [])
    } catch (portfolioError) {
      setError(portfolioError.message || 'Failed to load portfolio dashboard')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPortfolio()

    const intervalId = window.setInterval(() => {
      loadPortfolio()
    }, AUTO_REFRESH_MS)

    return () => window.clearInterval(intervalId)
  }, [])

  return (
    <main className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="rounded-3xl border border-white/40 bg-gradient-to-r from-purple-700 via-blue-700 to-emerald-500 p-6 text-white shadow-2xl shadow-purple-900/20">
          <p className="text-xs uppercase tracking-[0.2em] text-purple-100">Intelli-Credit</p>
          <h1 className="mt-2 text-3xl font-black tracking-tight md:text-4xl">Portfolio Risk Monitoring</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-200 md:text-base">
            Portfolio-level risk view across all analyzed companies, including exposure and alert signals.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <article className="glass-card gradient-outline feature-lift rounded-2xl p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">📉 Portfolio Risk</p>
            <p className="mt-2 text-2xl font-black text-slate-900">Balanced</p>
            <p className="text-xs text-amber-700">Monitor medium-risk cluster</p>
          </article>
          <article className="glass-card gradient-outline feature-lift rounded-2xl p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">💸 Loan Exposure</p>
            <p className="mt-2 text-2xl font-black text-slate-900">Live</p>
            <p className="text-xs text-slate-600">Auto-refresh every 15s</p>
          </article>
          <article className="glass-card gradient-outline feature-lift rounded-2xl p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">🧭 Category Tracking</p>
            <p className="mt-2 text-2xl font-black text-slate-900">Green / Yellow / Red</p>
            <p className="text-xs text-emerald-700">Policy aligned</p>
          </article>
          <article className="glass-card gradient-outline feature-lift rounded-2xl p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">🔔 Alert Engine</p>
            <p className="mt-2 text-2xl font-black text-slate-900">Real-time</p>
            <p className="text-xs text-purple-700">Risk triggers surfaced instantly</p>
          </article>
        </section>

        <div className="flex justify-end">
          <button
            type="button"
            onClick={loadPortfolio}
            disabled={loading}
            className="rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-md transition hover:scale-[1.03] disabled:cursor-not-allowed disabled:opacity-70"
          >
            {loading ? 'Refreshing...' : 'Refresh Portfolio'}
          </button>
        </div>

        {error && <p className="rounded-lg bg-rose-100 px-4 py-2 text-sm text-rose-700">{error}</p>}

        <section
          className={`rounded-2xl p-4 ring-1 ${
            alerts.length > 0 ? 'glass-card bg-rose-50 ring-rose-200' : 'glass-card bg-emerald-50 ring-emerald-200'
          }`}
        >
          <h3
            className={`text-sm font-bold uppercase tracking-[0.12em] ${
              alerts.length > 0 ? 'text-rose-800' : 'text-emerald-800'
            }`}
          >
            Risk Alerts
          </h3>
          {alerts.length > 0 ? (
            <ul className="mt-2 space-y-1 text-sm text-rose-700">
              {alerts.map((alert) => (
                <li key={alert}>{alert}</li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-sm text-emerald-700">No active alerts. Portfolio risk is within configured limits.</p>
          )}
        </section>

        <PortfolioStats summary={summary} />

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-1">
            <ExposureChart summary={summary} />
          </div>
          <div className="lg:col-span-2">
            <HighRiskTable records={highRiskRecords} />
          </div>
        </div>
      </div>
    </main>
  )
}
