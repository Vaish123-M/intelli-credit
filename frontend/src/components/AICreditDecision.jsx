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

function decisionTone(loanDecision) {
  if (loanDecision === 'Reject') return 'rose'
  if (loanDecision === 'Review') return 'amber'
  return 'green'
}

export default function AICreditDecision({
  decision,
  onGenerateCam,
  onGenerateFinalReport,
  isGeneratingCam,
  isGeneratingFinalReport,
  canGenerateCam,
}) {
  if (!decision) return null

  const factors = decision.top_risk_factors || []
  const reasoning = decision.reasoning || factors
  const swot = decision.swot_analysis || {}
  const strengths = swot.strengths || []
  const weaknesses = swot.weaknesses || []
  const opportunities = swot.opportunities || []
  const threats = swot.threats || []
  const tone = riskTone(decision.risk_category)
  const loanDecision = decision.loan_decision || (decision.decision_status === 'Approved' ? 'Approve' : decision.decision_status === 'Rejected' ? 'Reject' : 'Review')
  const explainTone = decisionTone(loanDecision)

  return (
    <section className="glass-card gradient-outline mt-8 space-y-4 rounded-2xl p-5">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-bold uppercase tracking-[0.12em] text-slate-700">AI Credit Decision</h3>
        <span className="rounded-full bg-linear-to-r from-purple-600 to-blue-600 px-3 py-1 text-xs font-semibold text-white">ML Risk Engine 🤖</span>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <DecisionCard title="Loan Decision" value={loanDecision} tone={explainTone} />
        <DecisionCard title="Risk Score" value={`${Math.round((decision.risk_score || 0) * 100)}%`} tone={tone} />
        <DecisionCard title="Risk Category" value={decision.risk_category || 'N/A'} tone={tone} />
        <DecisionCard title="Recommended Loan" value={decision.loan_limit || 'N/A'} />
        <DecisionCard title="Interest Rate" value={decision.interest_rate || 'N/A'} hint={decision.decision_status || ''} />
      </div>

      <div className="flex flex-wrap justify-end gap-2">
        <button
          type="button"
          onClick={onGenerateFinalReport}
          disabled={!canGenerateCam || isGeneratingFinalReport}
          className="rounded-xl bg-linear-to-r from-emerald-600 via-blue-600 to-slate-800 px-4 py-2 text-sm font-semibold text-white shadow-md transition hover:scale-[1.03] disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isGeneratingFinalReport ? 'Generating Final PDF...' : 'Download Final Report'}
        </button>
        <button
          type="button"
          onClick={onGenerateCam}
          disabled={!canGenerateCam || isGeneratingCam}
          className="rounded-xl bg-linear-to-r from-blue-600 via-purple-600 to-emerald-500 px-4 py-2 text-sm font-semibold text-white shadow-md transition hover:scale-[1.03] disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isGeneratingCam ? 'Generating CAM PDF...' : 'Download CAM Report'}
        </button>
      </div>

      <div className="rounded-xl bg-white p-4 ring-1 ring-slate-200">
        <p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-500">Explainable Reasoning</p>
        {reasoning.length > 0 ? (
          <ul className="mt-2 space-y-1 text-sm text-slate-700">
            {reasoning.map((item, index) => (
              <li key={`${item}-${index}`} className="rounded-lg bg-slate-50 px-3 py-2">
                {item}
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-2 text-sm text-slate-600">No reasoning available.</p>
        )}
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

      <div className="rounded-xl bg-white p-4 ring-1 ring-slate-200">
        <p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-500">SWOT Analysis</p>

        <div className="mt-2 grid gap-3 md:grid-cols-2">
          <div className="rounded-lg bg-emerald-50 p-3">
            <p className="text-xs font-semibold uppercase tracking-widest text-emerald-800">Strengths</p>
            <ul className="mt-2 space-y-1 text-sm text-slate-700">
              {(strengths.length ? strengths : ['No major strengths identified']).map((item, idx) => (
                <li key={`strength-${idx}`} className="rounded bg-white/70 px-2 py-1">{item}</li>
              ))}
            </ul>
          </div>

          <div className="rounded-lg bg-amber-50 p-3">
            <p className="text-xs font-semibold uppercase tracking-widest text-amber-800">Weaknesses</p>
            <ul className="mt-2 space-y-1 text-sm text-slate-700">
              {(weaknesses.length ? weaknesses : ['No major weaknesses identified']).map((item, idx) => (
                <li key={`weakness-${idx}`} className="rounded bg-white/70 px-2 py-1">{item}</li>
              ))}
            </ul>
          </div>

          <div className="rounded-lg bg-blue-50 p-3">
            <p className="text-xs font-semibold uppercase tracking-widest text-blue-800">Opportunities</p>
            <ul className="mt-2 space-y-1 text-sm text-slate-700">
              {(opportunities.length ? opportunities : ['No clear opportunities identified']).map((item, idx) => (
                <li key={`opportunity-${idx}`} className="rounded bg-white/70 px-2 py-1">{item}</li>
              ))}
            </ul>
          </div>

          <div className="rounded-lg bg-rose-50 p-3">
            <p className="text-xs font-semibold uppercase tracking-widest text-rose-800">Threats</p>
            <ul className="mt-2 space-y-1 text-sm text-slate-700">
              {(threats.length ? threats : ['No immediate threats identified']).map((item, idx) => (
                <li key={`threat-${idx}`} className="rounded bg-white/70 px-2 py-1">{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  )
}
