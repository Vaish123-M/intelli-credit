import { useEffect, useState } from 'react'

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

function StatCard({ label, value, tone, icon }) {
  const toneMap = {
    slate: 'from-slate-50 to-white ring-slate-200 text-slate-900',
    green: 'from-emerald-50 to-white ring-emerald-200 text-emerald-900',
    amber: 'from-amber-50 to-white ring-amber-200 text-amber-900',
    rose: 'from-rose-50 to-white ring-rose-200 text-rose-900',
  }

  const animatedValue = useAnimatedValue(value)

  return (
    <article className={`gradient-outline feature-lift rounded-2xl bg-gradient-to-br p-5 shadow-sm ring-1 ${toneMap[tone] || toneMap.slate}`}>
      <p className="text-xs font-bold uppercase tracking-[0.12em] opacity-70">{icon} {label}</p>
      <p className="mt-2 text-3xl font-black">{animatedValue}</p>
    </article>
  )
}

export default function DashboardStats({ summary }) {
  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Companies Analyzed" value={summary.companies_analyzed ?? 0} tone="slate" icon="🏦" />
      <StatCard label="Low Risk" value={summary.low_risk ?? 0} tone="green" icon="✅" />
      <StatCard label="Medium Risk" value={summary.medium_risk ?? 0} tone="amber" icon="⚠" />
      <StatCard label="High Risk" value={summary.high_risk ?? 0} tone="rose" icon="🚨" />
    </section>
  )
}
