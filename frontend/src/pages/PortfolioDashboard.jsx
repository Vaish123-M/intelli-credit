import { useEffect, useState } from 'react'

import ExposureChart from '../components/portfolio/ExposureChart'
import HighRiskTable from '../components/portfolio/HighRiskTable'
import PortfolioStats from '../components/portfolio/PortfolioStats'
import { getPortfolioAlerts, getPortfolioHighRisk, getPortfolioSummary } from '../services/api'

const AUTO_REFRESH_MS = 15000

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
      const [nextSummary, nextAlerts, nextHighRisk] = await Promise.all([
        getPortfolioSummary(),
        getPortfolioAlerts(),
        getPortfolioHighRisk(),
      ])
      setSummary(nextSummary || {})
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
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#fee2e2,#f8fafc_35%,#fef3c7_90%)] px-4 py-8">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="rounded-3xl bg-slate-900 p-6 text-white shadow-xl">
          <p className="text-xs uppercase tracking-[0.2em] text-rose-200">Intelli-Credit</p>
          <h1 className="mt-2 text-3xl font-black tracking-tight md:text-4xl">Portfolio Risk Monitoring</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-200 md:text-base">
            Portfolio-level risk view across all analyzed companies, including exposure and alert signals.
          </p>
        </header>

        <div className="flex justify-end">
          <button
            type="button"
            onClick={loadPortfolio}
            disabled={loading}
            className="rounded-xl bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-500 disabled:cursor-not-allowed disabled:bg-rose-300"
          >
            {loading ? 'Refreshing...' : 'Refresh Portfolio'}
          </button>
        </div>

        {error && <p className="rounded-lg bg-rose-100 px-4 py-2 text-sm text-rose-700">{error}</p>}

        <section
          className={`rounded-2xl p-4 ring-1 ${
            alerts.length > 0 ? 'bg-rose-50 ring-rose-200' : 'bg-emerald-50 ring-emerald-200'
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
