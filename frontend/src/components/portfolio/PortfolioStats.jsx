import { useEffect, useState } from 'react'

function formatExposure(value) {
  const numeric = Number(value || 0)
  if (numeric >= 10_000_000) return `INR ${(numeric / 10_000_000).toFixed(2)} Cr`
  if (numeric >= 100_000) return `INR ${(numeric / 100_000).toFixed(2)} L`
  return `INR ${Math.round(numeric).toLocaleString('en-IN')}`
}

function useAnimatedValue(targetValue) {
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    const safeTarget = Number(targetValue || 0)
    const duration = 680
    const steps = 26
    const stepValue = safeTarget / steps
    let current = 0

    const intervalId = window.setInterval(() => {
      current += 1
      const nextValue = Math.min(safeTarget, Math.round(stepValue * current))
      setDisplayValue(nextValue)

      if (current >= steps) {
        window.clearInterval(intervalId)
      }
    }, duration / steps)

    return () => window.clearInterval(intervalId)
  }, [targetValue])

  return displayValue
}

function StatCard({ label, value, tone = 'slate', icon }) {
  const toneMap = {
    slate: 'bg-white ring-slate-200 text-slate-900',
    blue: 'bg-sky-50 ring-sky-200 text-sky-900',
    green: 'bg-emerald-50 ring-emerald-200 text-emerald-900',
    amber: 'bg-amber-50 ring-amber-200 text-amber-900',
    rose: 'bg-rose-50 ring-rose-200 text-rose-900',
  }

  return (
    <article className={`gradient-outline feature-lift rounded-2xl p-5 shadow-sm ring-1 ${toneMap[tone] || toneMap.slate}`}>
      <p className="text-xs font-bold uppercase tracking-[0.12em] opacity-70">{icon} {label}</p>
      <p className="mt-2 text-2xl font-black">{value}</p>
    </article>
  )
}

export default function PortfolioStats({ summary }) {
  const companies = useAnimatedValue(summary.companies_analyzed ?? 0)
  const low = useAnimatedValue(summary.low_risk ?? 0)
  const medium = useAnimatedValue(summary.medium_risk ?? 0)
  const high = useAnimatedValue(summary.high_risk ?? 0)

  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
      <StatCard label="Companies Analyzed" value={companies} tone="slate" icon="🏦" />
      <StatCard label="Total Exposure" value={formatExposure(summary.total_exposure)} tone="blue" icon="💼" />
      <StatCard label="Low Risk" value={low} tone="green" icon="✅" />
      <StatCard label="Medium Risk" value={medium} tone="amber" icon="⚠" />
      <StatCard label="High Risk" value={high} tone="rose" icon="🚨" />
    </section>
  )
}
