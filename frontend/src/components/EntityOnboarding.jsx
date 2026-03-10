import { useMemo, useState } from 'react'

const STEPS = [
  { id: 1, label: 'Company Details' },
  { id: 2, label: 'Loan Details' },
  { id: 3, label: 'Continue' },
]

const LOAN_TYPES = ['Working Capital', 'Term Loan', 'Trade Finance']

const INITIAL_FORM = {
  company_name: '',
  cin: '',
  pan: '',
  sector: '',
  annual_turnover: '',
  loan_type: 'Working Capital',
  loan_amount: '',
  loan_tenure: '',
  interest_rate: '',
}

function StepPill({ step, activeStep, done }) {
  const isActive = step.id === activeStep
  const isDone = done || step.id < activeStep

  return (
    <div className="flex items-center gap-2">
      <div
        className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
          isDone
            ? 'bg-emerald-600 text-white'
            : isActive
            ? 'bg-blue-600 text-white'
            : 'bg-slate-200 text-slate-600'
        }`}
      >
        {isDone ? '✓' : step.id}
      </div>
      <span className={`text-xs font-semibold uppercase tracking-[0.09em] ${isActive ? 'text-slate-900' : 'text-slate-500'}`}>
        {step.label}
      </span>
    </div>
  )
}

function InputField({ label, name, value, onChange, placeholder, type = 'text', error }) {
  return (
    <label className="space-y-1">
      <span className="text-xs font-semibold uppercase tracking-[0.08em] text-slate-600">{label}</span>
      <input
        type={type}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full rounded-xl border bg-white px-3 py-2.5 text-sm outline-none focus:ring ${
          error ? 'border-rose-300 ring-rose-100' : 'border-slate-300 ring-blue-100'
        }`}
      />
      {error && <p className="text-xs text-rose-600">{error}</p>}
    </label>
  )
}

export default function EntityOnboarding({ onSubmit, onCompleted }) {
  const [step, setStep] = useState(1)
  const [form, setForm] = useState(INITIAL_FORM)
  const [errors, setErrors] = useState({})
  const [submitError, setSubmitError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [entityId, setEntityId] = useState('')
  const [isComplete, setIsComplete] = useState(false)

  const canGoBack = step > 1 && !isComplete

  const stepLabel = useMemo(() => STEPS.find((item) => item.id === step)?.label || '', [step])

  const updateField = (event) => {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
    setErrors((current) => ({ ...current, [name]: '' }))
  }

  const validateStep = (targetStep) => {
    const nextErrors = {}

    if (targetStep === 1) {
      if (!form.company_name.trim()) nextErrors.company_name = 'Company name is required.'
      if (!form.cin.trim()) nextErrors.cin = 'CIN is required.'
      if (!form.pan.trim()) nextErrors.pan = 'PAN is required.'
      if (!form.sector.trim()) nextErrors.sector = 'Sector is required.'
      if (!String(form.annual_turnover).trim()) nextErrors.annual_turnover = 'Annual turnover is required.'
    }

    if (targetStep === 2) {
      if (!form.loan_type.trim()) nextErrors.loan_type = 'Loan type is required.'
      if (!String(form.loan_amount).trim()) nextErrors.loan_amount = 'Loan amount is required.'
      if (!form.loan_tenure.trim()) nextErrors.loan_tenure = 'Loan tenure is required.'
      if (!String(form.interest_rate).trim()) nextErrors.interest_rate = 'Interest rate is required.'
    }

    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleNext = () => {
    setSubmitError('')
    if (!validateStep(step)) return
    setStep((current) => Math.min(current + 1, 3))
  }

  const handleBack = () => {
    setSubmitError('')
    setStep((current) => Math.max(current - 1, 1))
  }

  const handleSubmit = async () => {
    setSubmitError('')

    if (!validateStep(1) || !validateStep(2)) {
      setStep(1)
      return
    }

    setIsSubmitting(true)
    try {
      const payload = {
        ...form,
        annual_turnover: Number(form.annual_turnover),
        loan_amount: Number(form.loan_amount),
        interest_rate: Number(form.interest_rate),
      }

      const result = await onSubmit(payload)
      const nextEntityId = result?.entity_id || ''
      setEntityId(nextEntityId)
      setIsComplete(true)
      onCompleted?.(result)
    } catch (error) {
      setSubmitError(error.message || 'Failed to onboard entity.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isComplete) {
    return (
      <section className="glass-card rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
        <h3 className="text-sm font-bold uppercase tracking-[0.12em] text-emerald-800">Entity Onboarding Complete</h3>
        <p className="mt-2 text-sm text-emerald-700">Success! You can now continue to document upload and analysis.</p>
        <p className="mt-1 text-xs font-semibold text-emerald-900">Entity ID: {entityId}</p>
      </section>
    )
  }

  return (
    <section className="glass-card rounded-2xl p-5 ring-1 ring-white/60">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.12em] text-blue-700">Entity Onboarding</p>
          <h3 className="text-lg font-bold text-slate-900">Step {step}: {stepLabel}</h3>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          {STEPS.map((item) => (
            <StepPill key={item.id} step={item} activeStep={step} done={isComplete} />
          ))}
        </div>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {step === 1 && (
          <>
            <InputField
              label="Company Name"
              name="company_name"
              value={form.company_name}
              onChange={updateField}
              placeholder="Enter legal company name"
              error={errors.company_name}
            />
            <InputField label="CIN" name="cin" value={form.cin} onChange={updateField} placeholder="Enter CIN" error={errors.cin} />
            <InputField label="PAN" name="pan" value={form.pan} onChange={updateField} placeholder="Enter PAN" error={errors.pan} />
            <InputField label="Sector" name="sector" value={form.sector} onChange={updateField} placeholder="Enter sector" error={errors.sector} />
            <InputField
              label="Annual Turnover"
              name="annual_turnover"
              type="number"
              value={form.annual_turnover}
              onChange={updateField}
              placeholder="Enter annual turnover"
              error={errors.annual_turnover}
            />
          </>
        )}

        {step === 2 && (
          <>
            <label className="space-y-1">
              <span className="text-xs font-semibold uppercase tracking-[0.08em] text-slate-600">Loan Type</span>
              <select
                name="loan_type"
                value={form.loan_type}
                onChange={updateField}
                className={`w-full rounded-xl border bg-white px-3 py-2.5 text-sm outline-none focus:ring ${
                  errors.loan_type ? 'border-rose-300 ring-rose-100' : 'border-slate-300 ring-blue-100'
                }`}
              >
                {LOAN_TYPES.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
              {errors.loan_type && <p className="text-xs text-rose-600">{errors.loan_type}</p>}
            </label>

            <InputField
              label="Loan Amount"
              name="loan_amount"
              type="number"
              value={form.loan_amount}
              onChange={updateField}
              placeholder="Enter requested loan amount"
              error={errors.loan_amount}
            />
            <InputField
              label="Loan Tenure"
              name="loan_tenure"
              value={form.loan_tenure}
              onChange={updateField}
              placeholder="Example: 36 months"
              error={errors.loan_tenure}
            />
            <InputField
              label="Interest Rate"
              name="interest_rate"
              type="number"
              value={form.interest_rate}
              onChange={updateField}
              placeholder="Example: 11.5"
              error={errors.interest_rate}
            />
          </>
        )}

        {step === 3 && (
          <div className="md:col-span-2">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
              <p className="font-semibold text-slate-900">Review and continue to document upload</p>
              <p className="mt-2">Company: {form.company_name || '-'}</p>
              <p>CIN: {form.cin || '-'}</p>
              <p>PAN: {form.pan || '-'}</p>
              <p>Sector: {form.sector || '-'}</p>
              <p>Annual Turnover: {form.annual_turnover || '-'}</p>
              <p className="mt-2">Loan Type: {form.loan_type || '-'}</p>
              <p>Loan Amount: {form.loan_amount || '-'}</p>
              <p>Loan Tenure: {form.loan_tenure || '-'}</p>
              <p>Interest Rate: {form.interest_rate || '-'}</p>
            </div>
          </div>
        )}
      </div>

      {submitError && <p className="mt-4 rounded-lg bg-rose-100 px-3 py-2 text-sm text-rose-700">{submitError}</p>}

      <div className="mt-5 flex flex-wrap justify-end gap-2">
        {canGoBack && (
          <button
            type="button"
            onClick={handleBack}
            className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            Back
          </button>
        )}

        {step < 3 && (
          <button
            type="button"
            onClick={handleNext}
            className="rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-md transition hover:scale-[1.02]"
          >
            Next
          </button>
        )}

        {step === 3 && (
          <button
            type="button"
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="rounded-xl bg-gradient-to-r from-emerald-600 to-teal-500 px-4 py-2 text-sm font-semibold text-white shadow-md transition hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? 'Saving...' : 'Continue to Document Upload'}
          </button>
        )}
      </div>
    </section>
  )
}
