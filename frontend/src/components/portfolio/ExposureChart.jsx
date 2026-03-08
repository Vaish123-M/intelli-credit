function SegmentBar({ label, value, max, color }) {
  const width = max > 0 ? Math.round((value / max) * 100) : 0

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs text-slate-600">
        <span>{label}</span>
        <span className="font-semibold">{value}</span>
      </div>
      <div className="h-3 rounded-full bg-slate-100">
        <div className={`h-3 rounded-full ${color}`} style={{ width: `${width}%` }} />
      </div>
    </div>
  )
}

export default function ExposureChart({ summary }) {
  const low = Number(summary.low_risk || 0)
  const medium = Number(summary.medium_risk || 0)
  const high = Number(summary.high_risk || 0)
  const max = Math.max(low, medium, high, 1)

  return (
    <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <h3 className="text-sm font-bold uppercase tracking-[0.12em] text-slate-700">Portfolio Risk Distribution</h3>
      <p className="mt-1 text-xs text-slate-500">Risk spread across all analyzed companies</p>

      <div className="mt-4 space-y-4">
        <SegmentBar label="Low Risk" value={low} max={max} color="bg-emerald-500" />
        <SegmentBar label="Medium Risk" value={medium} max={max} color="bg-amber-500" />
        <SegmentBar label="High Risk" value={high} max={max} color="bg-rose-500" />
      </div>
    </section>
  )
}
