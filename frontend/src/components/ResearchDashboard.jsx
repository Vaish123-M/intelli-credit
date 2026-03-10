function IntelligenceCard({ title, value, hint, tone = 'slate' }) {
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

function asPercent(value) {
  if (typeof value !== 'number' || Number.isNaN(value)) return 'N/A'
  return `${Math.round(value * 100)}%`
}

export default function ResearchDashboard({ intelligence }) {
  if (!intelligence) return null

  const hasErrors = intelligence.errors && intelligence.errors.length > 0
  const recentNews = Array.isArray(intelligence.recent_news) ? intelligence.recent_news : []
  const sourcesUsed = intelligence.sources_used || {}

  return (
    <section className="glass-card gradient-outline mt-8 space-y-4 rounded-2xl p-5">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-bold uppercase tracking-[0.12em] text-slate-700">External Intelligence</h3>
        <span className="rounded-full bg-linear-to-r from-emerald-500 to-blue-600 px-3 py-1 text-xs font-semibold text-white">Secondary Research Engine</span>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <IntelligenceCard
          title="News Sentiment"
          value={asPercent(intelligence.negative_news_score || 0)}
          hint={`${intelligence.news_articles_found || 0} articles analyzed`}
          tone={(intelligence.negative_news_score || 0) > 0.5 ? 'rose' : 'green'}
        />

        <IntelligenceCard
          title="Litigation Cases"
          value={`${intelligence.litigation_cases || 0}`}
          hint={`High risk: ${intelligence.high_risk_cases || 0}`}
          tone={(intelligence.high_risk_cases || 0) > 0 ? 'rose' : 'amber'}
        />

        <IntelligenceCard
          title="Sector Risk"
          value={intelligence.sector_risk || 'Medium'}
          hint={intelligence.sector_outlook || `Detected sector: ${intelligence.sector || 'General'}`}
          tone={
            intelligence.sector_risk === 'High'
              ? 'rose'
              : intelligence.sector_risk === 'Low'
                ? 'green'
                : 'amber'
          }
        />

        <IntelligenceCard
          title="Market Sentiment"
          value={intelligence.market_sentiment || intelligence.promoter_sentiment || 'Neutral'}
          hint={intelligence.legal_risk || `Confidence: ${Math.round((intelligence.promoter_sentiment_confidence || 0) * 100)}%`}
          tone={
            (intelligence.market_sentiment || intelligence.promoter_sentiment) === 'Negative'
              ? 'rose'
              : (intelligence.market_sentiment || intelligence.promoter_sentiment) === 'Positive'
                ? 'green'
                : 'amber'
          }
        />
      </div>

      <div className="rounded-xl bg-white p-4 ring-1 ring-slate-200">
        <p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-500">Recent News Signals</p>
        {recentNews.length > 0 ? (
          <ul className="mt-2 space-y-1 text-sm text-slate-700">
            {recentNews.map((headline) => (
              <li key={headline} className="rounded-lg bg-slate-50 px-3 py-2">
                {headline}
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-2 text-sm text-slate-600">No recent headlines available.</p>
        )}
      </div>

      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded-xl bg-slate-50 p-3 text-xs text-slate-700 ring-1 ring-slate-200">
          <p className="font-semibold text-slate-900">Legal Risk</p>
          <p className="mt-1">{intelligence.legal_risk || 'No major litigation found'}</p>
        </div>
        <div className="rounded-xl bg-slate-50 p-3 text-xs text-slate-700 ring-1 ring-slate-200">
          <p className="font-semibold text-slate-900">Sector Outlook</p>
          <p className="mt-1">{intelligence.sector_outlook || 'Moderate growth expected'}</p>
        </div>
        <div className="rounded-xl bg-slate-50 p-3 text-xs text-slate-700 ring-1 ring-slate-200">
          <p className="font-semibold text-slate-900">Sources Used</p>
          <p className="mt-1">
            {sourcesUsed.news_api ? 'News API, ' : ''}
            {sourcesUsed.serpapi ? 'SerpAPI, ' : ''}
            {sourcesUsed.google_search_api ? 'Google Search API' : ''}
            {!sourcesUsed.news_api && !sourcesUsed.serpapi && !sourcesUsed.google_search_api ? 'Fallback dataset' : ''}
          </p>
        </div>
      </div>

      {hasErrors && (
        <div className="rounded-xl bg-amber-100 p-3 text-xs text-amber-900">
          <p className="font-semibold">Some external sources could not be reached:</p>
          <p className="mt-1">{intelligence.errors.join(' | ')}</p>
        </div>
      )}
    </section>
  )
}
