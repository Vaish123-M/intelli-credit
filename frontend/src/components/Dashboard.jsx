function MetricCard({ title, value, hint, tone = 'slate' }) {
  const toneClasses = {
    slate: 'ring-slate-200 bg-white',
    green: 'ring-emerald-200 bg-emerald-50',
    amber: 'ring-amber-200 bg-amber-50',
    rose: 'ring-rose-200 bg-rose-50',
  }

  return (
    <section className={`rounded-2xl p-5 shadow-sm ring-1 ${toneClasses[tone]}`}>
      <h3 className="text-xs font-bold uppercase tracking-[0.12em] text-slate-500">{title}</h3>
      <p className="mt-3 text-2xl font-black text-slate-900">{value}</p>
      {hint && <p className="mt-2 text-xs text-slate-600">{hint}</p>}
    </section>
  )
}

function formatCurrency(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return 'N/A'
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(value)
}

function formatRatio(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return 'N/A'
  return value.toFixed(2)
}

function formatPercentFromRatio(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return 'N/A'
  return `${(value * 100).toFixed(1)}%`
}

export default function Dashboard({ analysis }) {
  if (!analysis) {
    return null
  }

  const flags = analysis.risk_flags || []

  return (
    <div className="mt-8 space-y-4">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <MetricCard title="Revenue" value={`INR ${formatCurrency(analysis.revenue)}`} />
        <MetricCard
          title="Debt/Equity"
          value={formatRatio(analysis.debt_equity_ratio)}
          hint={analysis.debt_equity_ratio > 2 ? 'High leverage threshold crossed' : 'Within threshold'}
          tone={analysis.debt_equity_ratio > 2 ? 'rose' : 'green'}
        />
        <MetricCard
          title="EBITDA Margin"
          value={formatPercentFromRatio(analysis.ebitda_margin)}
          hint={analysis.ebitda_margin < 0.1 ? 'Profitability below 10%' : 'Profitability looks healthy'}
          tone={analysis.ebitda_margin < 0.1 ? 'amber' : 'green'}
        />
        <MetricCard
          title="GST Mismatch"
          value={analysis.gst_mismatch ? 'Yes' : 'No'}
          hint={`Difference: ${formatRatio(analysis.gst_difference_percent || 0)}%`}
          tone={analysis.gst_mismatch ? 'rose' : 'green'}
        />
        <MetricCard
          title="Bank Cashflow"
          value={`INR ${formatCurrency(analysis.bank_cashflow)}`}
          hint={`Credits: INR ${formatCurrency(analysis.bank_total_credits)} | Debits: INR ${formatCurrency(analysis.bank_total_debits)}`}
        />
        <MetricCard title="Revenue Growth" value={formatPercentFromRatio(analysis.revenue_growth)} />
      </div>

      <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
        <h3 className="text-xs font-bold uppercase tracking-[0.12em] text-slate-500">Risk Flags</h3>
        {flags.length > 0 ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {flags.map((flag) => (
              <span key={flag} className="rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold text-rose-800">
                {flag}
              </span>
            ))}
          </div>
        ) : (
          <p className="mt-3 text-sm text-emerald-700">No critical risk flags were detected.</p>
        )}
      </section>
    </div>
  )
}
