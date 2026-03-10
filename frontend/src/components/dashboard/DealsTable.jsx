function riskBadgeClass(riskCategory) {
  if (riskCategory === 'Low Risk') return 'bg-emerald-100 text-emerald-800'
  if (riskCategory === 'Medium Risk') return 'bg-amber-100 text-amber-800'
  return 'bg-rose-100 text-rose-800'
}

function statusBadgeClass(status) {
  if (status === 'Approved') return 'bg-emerald-100 text-emerald-800'
  if (status === 'Review Required') return 'bg-amber-100 text-amber-800'
  return 'bg-rose-100 text-rose-800'
}

export default function DealsTable({ deals }) {
  return (
    <section className="glass-card gradient-outline rounded-2xl p-4 shadow-sm ring-1 ring-slate-200">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-bold uppercase tracking-[0.12em] text-slate-700">Analyzed Deals</h3>
        <span className="text-xs text-slate-500">{deals.length} records</span>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Company Name</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Risk Score</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Risk Category</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Loan Limit</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Interest Rate</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Decision Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {deals.length > 0 ? (
              deals.map((deal) => (
                <tr key={`${deal.company_name}-${deal.timestamp}`} className="transition hover:bg-blue-50/50">
                  <td className="px-4 py-3 text-slate-800">{deal.company_name || 'Unknown Company'}</td>
                  <td className="px-4 py-3 text-slate-700">{Math.round((deal.risk_score || 0) * 100)}%</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${riskBadgeClass(deal.risk_category)}`}>
                      {deal.risk_category || 'N/A'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-700">{deal.loan_limit || 'N/A'}</td>
                  <td className="px-4 py-3 text-slate-700">{deal.interest_rate || 'N/A'}</td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${statusBadgeClass(deal.decision_status)}`}>
                      {deal.decision_status || 'N/A'}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-4 py-6 text-center text-slate-500" colSpan={6}>
                  No analyzed companies yet. Run Research + Risk Scoring from the underwriting page.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
