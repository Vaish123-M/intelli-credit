function formatLoanLimit(value) {
  const numeric = Number(value || 0)
  if (numeric >= 10_000_000) return `INR ${(numeric / 10_000_000).toFixed(2)} Cr`
  if (numeric >= 100_000) return `INR ${(numeric / 100_000).toFixed(2)} L`
  return `INR ${Math.round(numeric).toLocaleString('en-IN')}`
}

export default function HighRiskTable({ records }) {
  return (
    <section className="glass-card gradient-outline rounded-2xl p-4 shadow-sm ring-1 ring-slate-200">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-bold uppercase tracking-[0.12em] text-slate-700">High Risk Companies</h3>
        <span className="text-xs text-slate-500">{records.length} records</span>
      </div>

      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Company</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Risk Score</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Loan Limit</th>
              <th className="px-4 py-3 text-left font-semibold text-slate-700">Interest Rate</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {records.length > 0 ? (
              records.map((record) => (
                <tr key={`${record.company_name}-${record.timestamp}`} className="transition hover:bg-rose-50/40">
                  <td className="px-4 py-3 text-slate-800">{record.company_name || 'Unknown Company'}</td>
                  <td className="px-4 py-3 text-slate-700">{Math.round((record.risk_score || 0) * 100)}%</td>
                  <td className="px-4 py-3 text-slate-700">{formatLoanLimit(record.loan_limit)}</td>
                  <td className="px-4 py-3 text-slate-700">{record.interest_rate || 'N/A'}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-4 py-6 text-center text-slate-500" colSpan={4}>
                  No high-risk records detected in the portfolio.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  )
}
