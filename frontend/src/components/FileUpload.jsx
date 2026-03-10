import { useMemo } from 'react'
import { useDropzone } from 'react-dropzone'

const ACCEPTED_FILE_TYPES = {
  'text/csv': ['.csv'],
  'application/pdf': ['.pdf'],
}

const DOC_TYPES = [
  'ALM (Asset Liability Management)',
  'Shareholding Pattern',
  'Borrowing Profile',
  'Annual Report',
  'Portfolio Cuts / Performance Data',
]

function formatConfidence(value) {
  const numeric = Number(value || 0)
  return `${Math.round(numeric * 100)}%`
}

export default function FileUpload({
  files,
  onFilesSelected,
  onUpload,
  onClassify,
  classifications,
  onClassificationChange,
  onClassificationApproval,
  isUploading,
  isProcessing,
  isClassifying,
}) {
  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    accept: ACCEPTED_FILE_TYPES,
    multiple: true,
    onDrop: (acceptedFiles) => {
      onFilesSelected(acceptedFiles)
    },
  })

  const hasFiles = files.length > 0
  const hasClassifications = Array.isArray(classifications) && classifications.length > 0
  const allApproved = hasClassifications && classifications.every((item) => item.approved)

  const dropzoneClasses = useMemo(() => {
    const base =
      'rounded-2xl border-2 border-dashed p-8 transition-all duration-300 cursor-pointer bg-white/70 backdrop-blur-sm shadow-sm feature-lift'
    return isDragActive
      ? `${base} border-purple-500 bg-purple-50`
      : `${base} border-slate-300 hover:border-emerald-500 hover:bg-emerald-50/80`
  }, [isDragActive])

  return (
    <div className="space-y-4">
      <div {...getRootProps()} className={dropzoneClasses}>
        <input {...getInputProps()} />
        <p className="text-lg font-semibold text-slate-800">Drop GST/Bank CSVs and PDF reports here 📄</p>
        <p className="mt-2 text-sm text-slate-600">or click to select multiple files for AI analysis</p>
        <p className="mt-3 text-xs font-semibold uppercase tracking-[0.12em] text-slate-500">
          {isDragActive ? 'Release to upload into pipeline' : 'Supported: CSV and PDF'}
        </p>
      </div>

      {fileRejections.length > 0 && (
        <p className="rounded-lg bg-rose-100 px-4 py-2 text-sm text-rose-700">
          Some files were rejected. Please upload only CSV or PDF files.
        </p>
      )}

      {hasFiles && (
        <div className="rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
          <h3 className="mb-2 text-sm font-bold uppercase tracking-wide text-slate-500">Selected files</h3>
          <ul className="space-y-1 text-sm text-slate-700">
            {files.map((file) => (
              <li key={`${file.name}-${file.lastModified}`} className="flex items-center justify-between">
                <span className="truncate pr-4">{file.name}</span>
                <span className="text-slate-500">{(file.size / 1024).toFixed(1)} KB</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {hasClassifications && (
        <div className="rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
          <h3 className="mb-3 text-sm font-bold uppercase tracking-wide text-slate-500">Classification Results</h3>
          <div className="space-y-3">
            {classifications.map((item) => (
              <div key={item.file_name} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-slate-900">File: {item.file_name}</p>
                  <p className="text-xs font-semibold text-blue-700">Confidence: {formatConfidence(item.confidence)}</p>
                </div>

                <div className="mt-2 grid gap-3 md:grid-cols-[1fr_auto] md:items-center">
                  <div>
                    <label className="text-xs font-semibold uppercase tracking-[0.08em] text-slate-600">Detected Type</label>
                    <select
                      value={item.detected_type}
                      onChange={(event) => onClassificationChange(item.file_name, event.target.value)}
                      className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-800 outline-none ring-blue-100 focus:ring"
                    >
                      {DOC_TYPES.map((docType) => (
                        <option key={docType} value={docType}>
                          {docType}
                        </option>
                      ))}
                    </select>
                  </div>

                  <label className="inline-flex items-center gap-2 text-sm font-medium text-slate-700">
                    <input
                      type="checkbox"
                      checked={Boolean(item.approved)}
                      onChange={(event) => onClassificationApproval(item.file_name, event.target.checked)}
                      className="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
                    />
                    Approve
                  </label>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={onClassify}
          disabled={!hasFiles || isClassifying || isUploading || isProcessing}
          className="inline-flex items-center rounded-xl border border-blue-300 bg-blue-50 px-5 py-2.5 text-sm font-semibold text-blue-700 transition hover:bg-blue-100 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isClassifying ? 'Classifying...' : 'Classify Documents'}
        </button>

        <button
          type="button"
          onClick={onUpload}
          disabled={!hasFiles || !allApproved || isUploading || isProcessing || isClassifying}
          className="inline-flex items-center rounded-xl bg-gradient-to-r from-blue-600 via-purple-600 to-emerald-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:scale-[1.03] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isUploading ? 'Uploading files...' : isProcessing ? 'Processing...' : 'Upload and Analyze'}
        </button>
        {(isUploading || isProcessing || isClassifying) && (
          <span className="text-sm font-medium text-slate-600">AI processing in progress...</span>
        )}
        {hasFiles && !allApproved && <span className="text-sm font-medium text-amber-700">Approve classifications before upload.</span>}
      </div>
    </div>
  )
}
