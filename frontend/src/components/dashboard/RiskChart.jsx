import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function RiskChart({ summary }) {
  const low = Number(summary.low_risk || 0)
  const medium = Number(summary.medium_risk || 0)
  const high = Number(summary.high_risk || 0)
  const distribution = [
    { name: 'Low Risk', value: low, color: '#10b981' },
    { name: 'Medium Risk', value: medium, color: '#f59e0b' },
    { name: 'High Risk', value: high, color: '#ef4444' },
  ]

  return (
    <section className="glass-card gradient-outline rounded-2xl p-5">
      <h3 className="text-sm font-bold uppercase tracking-[0.12em] text-slate-700">Risk Distribution</h3>
      <p className="mt-1 text-xs text-slate-500">Live split of credit decisions by risk segment</p>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div className="h-52 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={distribution} dataKey="value" nameKey="name" innerRadius={56} outerRadius={82} stroke="none" paddingAngle={3}>
                {distribution.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="h-52 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={distribution} margin={{ top: 12, right: 8, left: -12, bottom: 8 }}>
              <XAxis dataKey="name" tickLine={false} axisLine={false} fontSize={11} />
              <YAxis allowDecimals={false} tickLine={false} axisLine={false} fontSize={11} />
              <Tooltip />
              <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                {distribution.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  )
}
