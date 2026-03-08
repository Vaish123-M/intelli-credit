function formatExposure(value) {
  const numeric = Number(value || 0)
  if (numeric >= 10_000_000) return `INR ${(numeric / 10_000_000).toFixed(2)} Cr`
  if (numeric >= 100_000) return `INR ${(numeric / 100_000).toFixed(2)} L`
  return `INR ${Math.round(numeric).toLocaleString('en-IN')}`
}

function StatCard({ label, value, tone = 'slate' }) {
  const toneMap = {
    slate: 'bg-white ring-slate-200 text-slate-900',
    blue: 'bg-sky-50 ring-sky-200 text-sky-900',
    green: 'bg-emerald-50 ring-emerald-200 text-emerald-900',
    amber: 'bg-amber-50 ring-amber-200 text-amber-900',
    rose: 'bg-rose-50 ring-rose-200 text-rose-900',
  }

  return (
    <article className={`rounded-2xl p-5 shadow-sm ring-1 ${toneMap[tone] || toneMap.slate}`}>
      <p className="text-xs font-bold uppercase tracking-[0.12em] opacity-70">{label}</p>
      <p className="mt-2 text-2xl font-black">{value}</p>
    </article>
  )
}

export default function PortfolioStats({ summary }) {
  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
      <StatCard label="Companies Analyzed" value={summary.companies_analyzed ?? 0} tone="slate" />
      <StatCard label="Total Exposure" value={formatExposure(summary.total_exposure)} tone="blue" />
      <StatCard label="Low Risk" value={summary.low_risk ?? 0} tone="green" />
      <StatCard label="Medium Risk" value={summary.medium_risk ?? 0} tone="amber" />
      <StatCard label="High Risk" value={summary.high_risk ?? 0} tone="rose" />
    </section>
  )
}
