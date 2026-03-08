import { useMemo, useState } from 'react'

import { askCopilotQuestion } from '../../services/api'

const SUGGESTED_QUESTIONS = [
  'Why is this company Medium Risk?',
  'What are the biggest financial risks?',
  'Should we approve this loan?',
]

export default function CopilotChat({ deals }) {
  const [selectedCompany, setSelectedCompany] = useState('')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const selectedDeal = useMemo(() => {
    if (!Array.isArray(deals) || deals.length === 0) return null
    const selected = deals.find((deal) => deal.company_name === selectedCompany)
    return selected || deals[0]
  }, [deals, selectedCompany])

  const handleAsk = async () => {
    const trimmedQuestion = question.trim()
    if (!selectedDeal) {
      setError('No analyzed companies available yet. Run scoring first.')
      return
    }
    if (!trimmedQuestion) {
      setError('Enter a question for the AI Copilot.')
      return
    }

    const companyData = {
      company_name: selectedDeal.company_name,
      financial_analysis: selectedDeal.financial_analysis || {},
      external_intelligence: selectedDeal.external_intelligence || {},
      risk_decision: selectedDeal.risk_decision || {
        risk_score: selectedDeal.risk_score,
        risk_category: selectedDeal.risk_category,
        loan_limit: selectedDeal.loan_limit,
        interest_rate: selectedDeal.interest_rate,
        decision_status: selectedDeal.decision_status,
      },
    }

    setError('')
    setIsLoading(true)
    try {
      const payload = await askCopilotQuestion({ companyData, question: trimmedQuestion })
      setAnswer(payload.answer || 'No response generated.')
    } catch (askError) {
      setError(askError.message || 'Copilot failed to answer.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-bold uppercase tracking-[0.12em] text-slate-700">AI Credit Copilot</h3>
        <span className="rounded-full bg-indigo-100 px-3 py-1 text-xs font-semibold text-indigo-700">Phase 7</span>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-[220px,1fr,auto]">
        <select
          value={selectedCompany}
          onChange={(event) => setSelectedCompany(event.target.value)}
          className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none ring-indigo-200 focus:ring"
        >
          {deals.length === 0 ? (
            <option value="">No companies available</option>
          ) : (
            deals.map((deal) => (
              <option key={`${deal.company_name}-${deal.timestamp}`} value={deal.company_name}>
                {deal.company_name}
              </option>
            ))
          )}
        </select>

        <input
          type="text"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask about risk, approval, or key drivers..."
          className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm text-slate-800 outline-none ring-indigo-200 focus:ring"
        />

        <button
          type="button"
          onClick={handleAsk}
          disabled={isLoading || deals.length === 0}
          className="rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-indigo-300"
        >
          {isLoading ? 'Thinking...' : 'Send'}
        </button>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {SUGGESTED_QUESTIONS.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => setQuestion(item)}
            className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-200"
          >
            {item}
          </button>
        ))}
      </div>

      {error && <p className="mt-4 rounded-lg bg-rose-100 px-3 py-2 text-sm text-rose-700">{error}</p>}

      <div className="mt-4 rounded-xl bg-slate-50 p-4 ring-1 ring-slate-200">
        <p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-500">Copilot Response</p>
        <p className="mt-2 whitespace-pre-wrap text-sm text-slate-700">
          {answer || 'Ask a question to get an AI explanation of this credit decision.'}
        </p>
      </div>
    </section>
  )
}
