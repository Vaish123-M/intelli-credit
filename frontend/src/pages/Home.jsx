import { useMemo, useState } from 'react'

import AICreditDecision from '../components/AICreditDecision'
import Dashboard from '../components/Dashboard'
import FileUpload from '../components/FileUpload'
import ResearchDashboard from '../components/ResearchDashboard'
import { generateCamReport, getApiBaseUrl, getResults, runAnalysis, runResearch, runRiskScore, uploadFiles } from '../services/api'

export default function Home() {
  const [selectedFiles, setSelectedFiles] = useState([])
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [extractedData, setExtractedData] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [research, setResearch] = useState(null)
  const [decision, setDecision] = useState(null)
  const [companyName, setCompanyName] = useState('')
  const [promoterName, setPromoterName] = useState('')
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
      const payload = await runRiskScore({ financialAnalysis, externalIntelligence })
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
    if (!selectedFiles.length) {
      setError('Please select at least one file before uploading.')
      return
    }

    setError('')
    setSuccess('')
    setIsUploading(true)
    setIsProcessing(true)

    try {
      const uploadResult = await uploadFiles(selectedFiles)
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
    setError('')
    setSuccess('')
    setIsProcessing(true)

    try {
      const analysisResult = await runAnalysis()
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
    setError('')
    setSuccess('')
    setIsProcessing(true)

    try {
      const latestResults = await getResults()
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

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#dcfce7,#f8fafc_35%,#fef3c7_90%)] px-4 py-8">
      <div className="mx-auto max-w-6xl">
        <header className="rounded-3xl bg-slate-900 p-6 text-white shadow-xl">
          <p className="text-xs uppercase tracking-[0.2em] text-emerald-200">Intelli-Credit</p>
          <h1 className="mt-2 text-3xl font-black tracking-tight md:text-4xl">
            AI Corporate Credit Decision Engine
          </h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-200 md:text-base">
            Milestone 1: File Upload, Data Extraction, and Basic Financial Analysis for GST, bank statements,
            annual reports, and financial statements.
          </p>
        </header>

        <section className="mt-6 rounded-2xl bg-white/70 p-6 shadow-lg backdrop-blur-sm ring-1 ring-slate-200">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-xl font-bold text-slate-900">Upload and Process Documents</h2>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleAnalyze}
                disabled={isUploading || isProcessing}
                className="rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:bg-emerald-300"
              >
                Re-run Analysis
              </button>
              <button
                type="button"
                onClick={handleLoadResults}
                disabled={isUploading || isProcessing}
                className="rounded-xl bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-amber-400 disabled:cursor-not-allowed disabled:bg-amber-200"
              >
                Load Latest Results
              </button>
            </div>
          </div>

          <div className="mt-5">
            <FileUpload
              files={selectedFiles}
              onFilesSelected={setSelectedFiles}
              onUpload={handleUpload}
              isUploading={isUploading}
              isProcessing={isProcessing || isResearching || isScoring || isGeneratingCam}
            />
          </div>

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
              disabled={isUploading || isProcessing || isResearching || isScoring || isGeneratingCam}
              className="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-indigo-300"
            >
              {isResearching ? 'Researching...' : 'Run Research Agent'}
            </button>
          </div>

          {statusLabel && <p className="mt-4 text-sm font-medium text-emerald-700">{statusLabel}</p>}
          {(isProcessing || isResearching || isScoring || isGeneratingCam) && (
            <div className="mt-3 flex items-center gap-2 text-sm text-slate-700">
              <span className="inline-block h-3 w-3 animate-pulse rounded-full bg-emerald-500" />
              {isGeneratingCam
                ? 'Formatting 5C report and rendering CAM PDF...'
                : isScoring
                ? 'Scoring AI credit risk and generating decision recommendations...'
                : isResearching
                ? 'Gathering external intelligence, litigation, sector risk, and sentiment...'
                : 'Processing documents and generating credit signals...'}
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
        </section>
      </div>
    </main>
  )
}
