import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'

import AILoader from '../components/AILoader'
import AICreditDecision from '../components/AICreditDecision'
import Dashboard from '../components/Dashboard'
import EntityOnboarding from '../components/EntityOnboarding'
import FileUpload from '../components/FileUpload'
import ResearchDashboard from '../components/ResearchDashboard'
import brandMark from '../assets/intelli-credit-mark.svg'
import useRevealOnScroll from '../hooks/useRevealOnScroll'
import { generateCamReport, getApiBaseUrl, getResults, onboardEntity, runAnalysis, runResearch, runRiskScore, uploadFiles } from '../services/api'

const FEATURE_CARDS = [
  { icon: '📄', title: 'Document Upload', description: 'Upload GST, bank statements, and financial reports in one secure flow.' },
  { icon: '📊', title: 'Financial Analysis', description: 'Extract key financial signals like leverage, cashflow, and margin trends.' },
  { icon: '🌐', title: 'External Intelligence', description: 'Run litigation, sentiment, sector, and promoter checks automatically.' },
  { icon: '🤖', title: 'AI Risk Scoring', description: 'Generate explainable risk score, category, and lending recommendation.' },
  { icon: '📝', title: 'Credit Report Generation', description: 'Produce downloadable CAM report with rationale and risk narrative.' },
  { icon: '📈', title: 'Portfolio Monitoring', description: 'Track aggregate risk mix and identify high-risk exposure in real time.' },
]

const WORKFLOW_STEPS = [
  { id: '01', label: 'Upload docs', icon: '📄', detail: 'GST, bank statements, and financials' },
  { id: '02', label: 'Extract & analyze', icon: '📊', detail: 'Parse metrics and compute key ratios' },
  { id: '03', label: 'Research intelligence', icon: '🌐', detail: 'Pull litigation, sector, and sentiment' },
  { id: '04', label: 'AI risk scoring', icon: '🤖', detail: 'Generate explainable risk class and score' },
  { id: '05', label: 'Generate CAM report', icon: '📝', detail: 'Create downloadable credit memo output' },
]

function RevealSection({ children, className = '', delay = 0 }) {
  const { ref, controls } = useRevealOnScroll()

  return (
    <motion.section
      ref={ref}
      className={className}
      variants={{
        hidden: { opacity: 0, y: 28 },
        visible: { opacity: 1, y: 0 },
      }}
      initial="hidden"
      animate={controls}
      transition={{ duration: 0.55, ease: 'easeOut', delay }}
    >
      {children}
    </motion.section>
  )
}

function AnimatedStat({ value, label }) {
  return (
    <div className="glass-card rounded-2xl p-4 text-center">
      <p className="animated-gradient bg-gradient-to-r from-blue-600 via-purple-600 to-emerald-500 bg-clip-text text-2xl font-black text-transparent md:text-3xl">
        {value}
      </p>
      <p className="mt-1 text-xs font-semibold uppercase tracking-[0.13em] text-slate-600">{label}</p>
    </div>
  )
}

export default function Home() {
  const [selectedFiles, setSelectedFiles] = useState([])
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [extractedData, setExtractedData] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [research, setResearch] = useState(null)
  const [decision, setDecision] = useState(null)
  const [companyName, setCompanyName] = useState('')
  const [promoterName, setPromoterName] = useState('')
  const [entityId, setEntityId] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isResearching, setIsResearching] = useState(false)
  const [isScoring, setIsScoring] = useState(false)
  const [isGeneratingCam, setIsGeneratingCam] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const statusLabel = useMemo(() => {
    if (isUploading) return 'Uploading files to backend...'
    if (isProcessing) return 'Running extraction and financial analysis...'
    if (isResearching) return 'Running external research agent...'
    if (isScoring) return 'Running AI credit risk model...'
    if (isGeneratingCam) return 'Generating credit approval memo report...'
    return ''
  }, [isUploading, isProcessing, isResearching, isScoring, isGeneratingCam])

  const handleGenerateCam = async () => {
    const finalCompanyName = companyName.trim() || 'Intelli Credit Applicant'
    if (!analysis || !research || !decision) {
      setError('Run financial analysis, research, and AI scoring before generating CAM report.')
      return
    }

    setError('')
    setIsGeneratingCam(true)
    try {
      const payload = await generateCamReport({
        companyName: finalCompanyName,
        financialAnalysis: analysis,
        externalIntelligence: research,
        riskDecision: decision,
      })

      const camPath = payload.cam_report_url
      if (!camPath) {
        throw new Error('CAM report URL not returned by server.')
      }

      const downloadUrl = camPath.startsWith('http') ? camPath : `${getApiBaseUrl()}${camPath}`
      window.open(downloadUrl, '_blank', 'noopener,noreferrer')
      setSuccess('CAM report generated successfully. Download started.')
    } catch (camError) {
      setError(camError.message || 'CAM report generation failed')
    } finally {
      setIsGeneratingCam(false)
    }
  }

  const runScoring = async (financialAnalysis, externalIntelligence, { silent = false } = {}) => {
    if (!financialAnalysis || !externalIntelligence) {
      return null
    }

    setIsScoring(true)
    try {
      const payload = await runRiskScore({
        companyName: companyName.trim() || 'Unknown Company',
        financialAnalysis,
        externalIntelligence,
      })
      setDecision(payload || null)
      if (!silent) {
        setSuccess('AI credit decision generated successfully.')
      }
      return payload
    } catch (scoringError) {
      setError(scoringError.message || 'Risk scoring failed')
      return null
    } finally {
      setIsScoring(false)
    }
  }

  const handleResearch = async ({ silent = false } = {}) => {
    const trimmedCompany = companyName.trim()
    if (!trimmedCompany) {
      if (!silent) setError('Enter company name to run external intelligence research.')
      return null
    }

    setError('')
    setIsResearching(true)
    try {
      const payload = await runResearch({ companyName: trimmedCompany, promoterName: promoterName.trim() })
      const nextResearch = payload.external_intelligence || null
      const nextAnalysis = payload.financial_analysis || analysis

      setResearch(nextResearch)
      if (payload.financial_analysis) {
        setAnalysis(nextAnalysis)
      }
      if (nextAnalysis && nextResearch) {
        await runScoring(nextAnalysis, nextResearch, { silent: true })
      }
      if (!silent) {
        setSuccess('External intelligence scan completed successfully.')
      }
      return payload.external_intelligence || null
    } catch (researchError) {
      setError(researchError.message || 'Research agent failed')
      return null
    } finally {
      setIsResearching(false)
    }
  }

  const handleUpload = async () => {
    if (!entityId) {
      setError('Please complete entity onboarding before document upload.')
      return
    }

    if (!selectedFiles.length) {
      setError('Please select at least one file before uploading.')
      return
    }

    setError('')
    setSuccess('')
    setIsUploading(true)
    setIsProcessing(true)

    try {
      const uploadResult = await uploadFiles(selectedFiles, entityId)
      setUploadedFiles(uploadResult.uploaded_files || [])
      setExtractedData(uploadResult.extracted_data || [])
      setAnalysis(uploadResult.analysis || null)
      setSuccess('Files uploaded and credit analysis completed successfully.')

      if (companyName.trim()) {
        await handleResearch({ silent: true })
      }
    } catch (uploadError) {
      setError(uploadError.message || 'Upload failed')
    } finally {
      setIsUploading(false)
      setIsProcessing(false)
    }
  }

  const handleAnalyze = async () => {
    if (!entityId) {
      setError('Please complete entity onboarding before analysis.')
      return
    }

    setError('')
    setSuccess('')
    setIsProcessing(true)

    try {
      const analysisResult = await runAnalysis(entityId)
      setAnalysis(analysisResult.analysis || null)
      setDecision(null)
      if (analysisResult.extracted_data) {
        setExtractedData(analysisResult.extracted_data)
      }
      setSuccess('Financial analysis completed successfully.')
    } catch (analysisError) {
      setError(analysisError.message || 'Analysis failed')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleLoadResults = async () => {
    if (!entityId) {
      setError('Please complete entity onboarding before loading results.')
      return
    }

    setError('')
    setSuccess('')
    setIsProcessing(true)

    try {
      const latestResults = await getResults(entityId)
      setUploadedFiles(latestResults.uploaded_files || [])
      setExtractedData(latestResults.extracted_data || [])
      setAnalysis(latestResults.analysis || null)
      setDecision(null)
      setSuccess('Latest processed results loaded.')
    } catch (resultsError) {
      setError(resultsError.message || 'Could not load results')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleEntityOnboard = async (payload) => {
    const response = await onboardEntity(payload)
    setEntityId(response.entity_id || '')
    if (payload.company_name && !companyName.trim()) {
      setCompanyName(payload.company_name)
    }
    setError('')
    setSuccess('Entity onboarding completed. Continue with document upload.')
    return response
  }

  return (
    <main className="min-h-screen px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <RevealSection className="relative overflow-hidden rounded-3xl border border-white/50 p-6 sm:p-8 lg:p-10 animated-gradient bg-gradient-to-br from-blue-600/95 via-purple-600/95 to-emerald-500/90 text-white shadow-2xl shadow-blue-700/25">
          <div className="absolute -right-24 -top-24 h-56 w-56 rounded-full bg-white/10" />
          <div className="absolute -bottom-24 left-16 h-56 w-56 rounded-full bg-emerald-100/20" />

          <div className="relative z-10">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.26em] text-blue-100">🏦 Intelli-Credit Platform</p>
              <h2 className="mt-3 text-3xl font-extrabold leading-tight sm:text-4xl lg:text-5xl">
                AI-Powered Corporate Credit Risk Intelligence
              </h2>
              <p className="mt-4 max-w-2xl text-sm text-blue-50 sm:text-base">
                Upload financial documents and instantly receive an AI-driven credit decision with explainable risk insights.
                Built for modern underwriting teams that need speed, control, and confidence.
              </p>

              <div className="mt-6 grid gap-3 sm:grid-cols-3">
                <AnimatedStat value="10x faster" label="Credit analysis" />
                <AnimatedStat value="AI-driven" label="Risk insights" />
                <AnimatedStat value="Auto CAM" label="Report generation" />
              </div>
            </div>
          </div>
        </RevealSection>

        <RevealSection className="grid gap-5 lg:grid-cols-2" delay={0.05}>
          <article className="glass-card gradient-outline feature-lift rounded-3xl p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-700">Problem Overview</p>
            <h3 className="mt-2 text-2xl font-extrabold text-slate-900">Manual credit review is slow and inconsistent 📊</h3>
            <p className="mt-3 text-sm leading-relaxed text-slate-700">
              Corporate lending decisions rely on scattered data, delayed external checks, and subjective interpretation.
              This increases turnaround time and hidden risk across portfolios.
            </p>
          </article>

          <article className="glass-card gradient-outline feature-lift rounded-3xl p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">Solution</p>
            <h3 className="mt-2 text-2xl font-extrabold text-slate-900">Unified AI underwriting workflow 💼</h3>
            <p className="mt-3 text-sm leading-relaxed text-slate-700">
              Intelli-Credit combines document extraction, financial diagnostics, external intelligence, and AI risk scoring
              into one guided workflow designed for corporate credit analysts.
            </p>
          </article>
        </RevealSection>

        <RevealSection className="space-y-4" delay={0.08}>
          <div className="flex flex-wrap items-end justify-between gap-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-purple-700">Key Features</p>
              <h3 className="text-2xl font-extrabold text-slate-900">Fintech + AI capabilities for decision teams</h3>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {FEATURE_CARDS.map((feature) => (
              <motion.article
                key={feature.title}
                className="glass-card gradient-outline feature-lift rounded-2xl p-5"
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-10% 0px' }}
                transition={{ duration: 0.35 }}
              >
                <p className="text-2xl">{feature.icon}</p>
                <h4 className="mt-2 text-lg font-bold text-slate-900">{feature.title}</h4>
                <p className="mt-2 text-sm text-slate-700">{feature.description}</p>
              </motion.article>
            ))}
          </div>
        </RevealSection>

        <RevealSection className="glass-card rounded-3xl p-6" delay={0.1}>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-sky-700">Demo Workflow</p>
          <h3 className="mt-2 text-2xl font-extrabold text-slate-900">From upload to decision in minutes</h3>
          <div className="workflow-flowchart mt-5">
            {WORKFLOW_STEPS.map((step, index) => (
              <div key={step.id} className="workflow-flowchart-item">
                <article className="workflow-node">
                  <p className="workflow-node-id">Step {step.id}</p>
                  <h4 className="mt-1 text-sm font-extrabold text-slate-900 sm:text-base">
                    {step.label} <span aria-hidden="true">{step.icon}</span>
                  </h4>
                  <p className="mt-1 text-xs text-slate-600">{step.detail}</p>
                </article>

                {index < WORKFLOW_STEPS.length - 1 && (
                  <div className="workflow-arrow" aria-hidden="true">
                    <span className="workflow-arrow-right">→</span>
                    <span className="workflow-arrow-down">↓</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </RevealSection>

        <RevealSection className="glass-card rounded-3xl p-6 shadow-lg ring-1 ring-white/60" delay={0.12}>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-xl font-bold text-slate-900">Underwriting Studio</h2>
            <img src={brandMark} alt="Intelli-Credit logo" className="h-9 w-auto" />
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={!entityId || isUploading || isProcessing}
                className="rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-md transition hover:scale-[1.03] disabled:cursor-not-allowed disabled:opacity-70"
              >
                Re-run Analysis
              </button>
              <button
                type="button"
                onClick={handleLoadResults}
                disabled={!entityId || isUploading || isProcessing}
                className="rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 px-4 py-2 text-sm font-semibold text-white shadow-md transition hover:scale-[1.03] disabled:cursor-not-allowed disabled:opacity-70"
              >
                Load Latest Results
              </button>
            </div>
          </div>

          <div className="mt-5">
            <EntityOnboarding onSubmit={handleEntityOnboard} onCompleted={() => {}} />
          </div>

          <div className="mt-5">
            <FileUpload
              files={selectedFiles}
              onFilesSelected={setSelectedFiles}
              onUpload={handleUpload}
              isUploading={isUploading}
              isProcessing={!entityId || isProcessing || isResearching || isScoring || isGeneratingCam}
            />
          </div>

          {entityId && <p className="mt-2 text-xs font-medium text-slate-600">Active Entity ID: {entityId}</p>}

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <input
              type="text"
              value={companyName}
              onChange={(event) => setCompanyName(event.target.value)}
              placeholder="Company name (required for research)"
              className="rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-800 outline-none ring-emerald-200 focus:ring"
            />
            <input
              type="text"
              value={promoterName}
              onChange={(event) => setPromoterName(event.target.value)}
              placeholder="Promoter name (optional)"
              className="rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-800 outline-none ring-emerald-200 focus:ring"
            />
            <button
              type="button"
              onClick={() => handleResearch()}
              disabled={!entityId || isUploading || isProcessing || isResearching || isScoring || isGeneratingCam}
              className="rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-md transition hover:scale-[1.03] disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isResearching ? 'Researching...' : 'Run Research Agent'}
            </button>
          </div>

          {statusLabel && <p className="mt-4 text-sm font-medium text-emerald-700">AI analyzing financial data... 🤖 {statusLabel}</p>}
          {(isProcessing || isResearching || isScoring || isGeneratingCam) && (
            <div className="mt-3 space-y-2 text-sm text-slate-700">
              <AILoader
                label={
                  isGeneratingCam
                    ? 'Formatting 5C report and rendering CAM PDF...'
                    : isScoring
                    ? 'Scoring AI credit risk and generating decision recommendations...'
                    : isResearching
                    ? 'Gathering external intelligence, litigation, sector risk, and sentiment...'
                    : 'Processing documents and generating credit signals...'
                }
              />
            </div>
          )}
          {error && <p className="mt-4 rounded-lg bg-rose-100 px-4 py-2 text-sm text-rose-700">{error}</p>}
          {success && <p className="mt-4 rounded-lg bg-emerald-100 px-4 py-2 text-sm text-emerald-800">{success}</p>}

          <Dashboard analysis={analysis} />
          <ResearchDashboard intelligence={research} />
          <AICreditDecision
            decision={decision}
            onGenerateCam={handleGenerateCam}
            isGeneratingCam={isGeneratingCam}
            canGenerateCam={Boolean(analysis && research && decision)}
          />

          {!!uploadedFiles.length && (
            <p className="mt-4 text-xs text-slate-500">
              Processed files: {uploadedFiles.map((file) => file.filename).join(', ')}
            </p>
          )}

          {!!extractedData.length && (
            <p className="mt-1 text-xs text-slate-500">Parsed documents: {extractedData.length}</p>
          )}
        </RevealSection>

        <RevealSection className="rounded-3xl border border-white/40 bg-gradient-to-r from-blue-600 via-purple-600 to-emerald-500 p-6 text-white shadow-2xl shadow-purple-800/25" delay={0.13}>
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-100">Call to Action</p>
              <h3 className="mt-1 text-2xl font-extrabold">Ready to transform credit decisioning?</h3>
              <p className="mt-2 max-w-2xl text-sm text-blue-100">
                Launch a complete AI-assisted underwriting demo with real financial data, explainable risk decisions, and portfolio intelligence.
              </p>
            </div>
            <button
              type="button"
              onClick={handleUpload}
              disabled={!entityId || !selectedFiles.length || isUploading || isProcessing}
              className="rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-slate-900 shadow-md transition hover:scale-[1.04] disabled:cursor-not-allowed disabled:opacity-70"
            >
              Start AI Analysis
            </button>
          </div>
        </RevealSection>

        <RevealSection className="glass-card rounded-3xl p-6" delay={0.14}>
          <div className="grid gap-4 text-sm text-slate-700 md:grid-cols-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Project</p>
              <p className="mt-2 font-semibold text-slate-900">Intelli-Credit</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Repository</p>
              <p className="mt-2 break-all">github.com/Vaish123-M/intelli-credit</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Team</p>
              <p className="mt-2">AL-ML Vivitri Hack IITH</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Stack</p>
              <p className="mt-2">React + Vite + TailwindCSS + FastAPI</p>
            </div>
          </div>
        </RevealSection>
      </div>
    </main>
  )
}
