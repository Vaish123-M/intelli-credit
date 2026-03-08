function DecisionCard({ title, value, hint, tone = 'slate' }) {
  const toneClass = {
    slate: 'bg-white ring-slate-200',
    green: 'bg-emerald-50 ring-emerald-200',
    amber: 'bg-amber-50 ring-amber-200',
    rose: 'bg-rose-50 ring-rose-200',
  }

  return (
    <section className={`rounded-2xl p-5 shadow-sm ring-1 ${toneClass[tone]}`}>
      <h4 className="text-xs font-bold uppercase tracking-[0.12em] text-slate-500">{title}</h4>
      <p className="mt-2 text-2xl font-black text-slate-900">{value}</p>
      {hint && <p className="mt-2 text-xs text-slate-600">{hint}</p>}
    </section>
  )
}

function riskTone(riskCategory) {
  if (riskCategory === 'Reject') return 'rose'
  if (riskCategory === 'High Risk') return 'rose'
  if (riskCategory === 'Medium Risk') return 'amber'
  return 'green'
}

export default function AICreditDecision({ decision, onGenerateCam, isGeneratingCam, canGenerateCam }) {
  if (!decision) return null

  const factors = decision.top_risk_factors || []
  const tone = riskTone(decision.risk_category)

  return (
    <section className="mt-8 space-y-4 rounded-2xl bg-slate-50 p-5 ring-1 ring-slate-200">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-bold uppercase tracking-[0.12em] text-slate-700">AI Credit Decision</h3>
        <span className="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white">ML Risk Engine</span>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <DecisionCard title="Risk Score" value={`${Math.round((decision.risk_score || 0) * 100)}%`} tone={tone} />
        <DecisionCard title="Risk Category" value={decision.risk_category || 'N/A'} tone={tone} />
        <DecisionCard title="Recommended Loan" value={decision.loan_limit || 'N/A'} />
        <DecisionCard title="Interest Rate" value={decision.interest_rate || 'N/A'} />
      </div>

      <div className="flex justify-end">
        <button
          type="button"
          onClick={onGenerateCam}
          disabled={!canGenerateCam || isGeneratingCam}
          className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {isGeneratingCam ? 'Generating CAM PDF...' : 'Download CAM Report'}
        </button>
      </div>

      <div className="rounded-xl bg-white p-4 ring-1 ring-slate-200">
        <p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-500">Top Risk Factors</p>
        {factors.length > 0 ? (
          <ul className="mt-2 space-y-1 text-sm text-slate-700">
            {factors.map((factor) => (
              <li key={factor} className="rounded-lg bg-slate-50 px-3 py-2">
                {factor}
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-2 text-sm text-slate-600">No significant risk drivers detected.</p>
        )}
      </div>
    </section>
  )
}
