import { useEffect, useState } from 'react'

import DashboardStats from '../components/dashboard/DashboardStats'
import DealsTable from '../components/dashboard/DealsTable'
import RiskChart from '../components/dashboard/RiskChart'
import CopilotChat from '../components/dashboard/CopilotChat'
import { getDashboardDeals, getDashboardSummary } from '../services/api'

const AUTO_REFRESH_MS = 10000

function buildSummaryFromDeals(deals) {
  const normalizedDeals = Array.isArray(deals) ? deals : []

  const companiesAnalyzed = normalizedDeals.length
  const lowRisk = normalizedDeals.filter((deal) => deal.risk_category === 'Low Risk').length
  const mediumRisk = normalizedDeals.filter((deal) => deal.risk_category === 'Medium Risk').length
  const highRisk = normalizedDeals.filter((deal) => deal.risk_category === 'High Risk').length

  return {
    companies_analyzed: companiesAnalyzed,
    low_risk: lowRisk,
    medium_risk: mediumRisk,
    high_risk: highRisk,
  }
}

export default function CreditDashboard() {
  const [summary, setSummary] = useState({
    companies_analyzed: 0,
    low_risk: 0,
    medium_risk: 0,
    high_risk: 0,
  })
  const [dashboardStats, setDashboardStats] = useState({
    avg_risk_score: 0,
    recommendation: 'N/A',
    avg_interest: 'N/A',
  })
  const [deals, setDeals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadDashboard = async () => {
    setError('')
    setLoading(true)
    try {
      const [nextDeals, summaryData] = await Promise.all([
        getDashboardDeals(),
        getDashboardSummary(),
      ])
      const normalizedDeals = Array.isArray(nextDeals) ? nextDeals : []
      setDeals(normalizedDeals)
      setSummary(buildSummaryFromDeals(normalizedDeals))
      
      // Calculate derived stats from deals
      if (normalizedDeals.length > 0) {
        const avgRiskScore = normalizedDeals.reduce((sum, deal) => sum + (deal.risk_score || 0), 0) / normalizedDeals.length
        
        // Determine recommendation based on most common loan decision
        const decisionCounts = {}
        normalizedDeals.forEach(deal => {
          const decision = deal.loan_decision || 'Unknown'
          decisionCounts[decision] = (decisionCounts[decision] || 0) + 1
        })
        const mostCommonDecision = Object.entries(decisionCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A'
        
        // Calculate average interest rate
        const interestRates = normalizedDeals
          .map(deal => {
            const rateStr = deal.interest_rate || '0%'
            const rateNum = parseFloat(rateStr.replace('%', ''))
            return isNaN(rateNum) ? 0 : rateNum
          })
          .filter(rate => rate > 0)
        const avgInterest = interestRates.length > 0 
          ? (interestRates.reduce((sum, rate) => sum + rate, 0) / interestRates.length).toFixed(1) + '%'
          : 'N/A'
        
        setDashboardStats({
          avg_risk_score: avgRiskScore.toFixed(2),
          recommendation: mostCommonDecision,
          avg_interest: avgInterest,
        })
      }
    } catch (dashboardError) {
      setError(dashboardError.message || 'Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboard()

    const intervalId = window.setInterval(() => {
      loadDashboard()
    }, AUTO_REFRESH_MS)

    return () => window.clearInterval(intervalId)
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
            <p className="mt-2 text-2xl font-black text-slate-900">{dashboardStats.avg_risk_score}</p>
            <p className="text-xs text-amber-700">
              {dashboardStats.avg_risk_score > 0.6 ? 'High Risk ⚠' : dashboardStats.avg_risk_score > 0.4 ? 'Medium Risk ⚠' : 'Low Risk ✓'}
            </p>
          </article>
          <article className="glass-card gradient-outline feature-lift rounded-2xl p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">✅ Recommendation</p>
            <p className="mt-2 text-2xl font-black text-slate-900">{dashboardStats.recommendation}</p>
            <p className="text-xs text-purple-700">Policy + AI blended</p>
          </article>
          <article className="glass-card gradient-outline feature-lift rounded-2xl p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">💰 Avg Interest</p>
            <p className="mt-2 text-2xl font-black text-slate-900">{dashboardStats.avg_interest}</p>
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
