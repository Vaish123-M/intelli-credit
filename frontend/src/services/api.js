const ENV_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

let ACTIVE_API_BASE_URL = ENV_API_BASE_URL || 'http://127.0.0.1:8000'

function buildCandidateUrls() {
  const candidates = new Set()

  if (ENV_API_BASE_URL) {
    candidates.add(ENV_API_BASE_URL)
  }

  if (typeof window !== 'undefined') {
    const { protocol, hostname } = window.location
    const resolvedHost = hostname || '127.0.0.1'
    const resolvedProtocol = protocol === 'https:' ? 'https:' : 'http:'

    candidates.add(`${resolvedProtocol}//${resolvedHost}:8000`)
    candidates.add('http://127.0.0.1:8000')
    candidates.add('http://localhost:8000')
  } else {
    candidates.add('http://127.0.0.1:8000')
  }

  return Array.from(candidates)
}

export function getApiBaseUrl() {
  return ACTIVE_API_BASE_URL
}

async function parseResponse(response) {
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = payload?.detail || payload?.message || 'Request failed'
    throw new Error(message)
  }
  return payload
}

async function requestJson(path, options = {}) {
  const candidates = buildCandidateUrls()
  let lastError = null

  for (const baseUrl of candidates) {
    try {
      const response = await fetch(`${baseUrl}${path}`, options)
      ACTIVE_API_BASE_URL = baseUrl
      return await parseResponse(response)
    } catch (error) {
      lastError = error
      if (!(error instanceof TypeError)) {
        throw error
      }
    }
  }

  if (lastError instanceof TypeError) {
    throw new Error('Could not connect to backend API. Please ensure backend is running and reachable on port 8000.')
  }

  throw lastError || new Error('Request failed')
}

export async function onboardEntity(entityData) {
  return requestJson('/entity-onboard', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(entityData || {}),
  })
}

export async function uploadFiles(files, entityId) {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))
  formData.append('entity_id', entityId || '')

  return requestJson('/upload', {
    method: 'POST',
    body: formData,
  })
}

export async function runAnalysis(entityId) {
  const query = entityId ? `?entity_id=${encodeURIComponent(entityId)}` : ''
  const payload = await requestJson(`/analyze${query}`, {
    method: 'POST',
  })

  if (payload.analysis) {
    return payload
  }

  const { extracted_data: extractedData, ...analysis } = payload
  return { analysis, extracted_data: extractedData || [] }
}

export async function getResults(entityId) {
  const query = entityId ? `?entity_id=${encodeURIComponent(entityId)}` : ''
  return requestJson(`/results${query}`)
}

export async function runResearch({ companyName, promoterName }) {
  return requestJson('/research', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      company_name: companyName,
      promoter_name: promoterName || null,
    }),
  })
}

export async function runRiskScore({ companyName, financialAnalysis, externalIntelligence }) {
  return requestJson('/risk-score', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      company_name: companyName || 'Unknown Company',
      financial_analysis: financialAnalysis || {},
      external_intelligence: externalIntelligence || {},
    }),
  })
}

export async function generateCamReport({ companyName, financialAnalysis, externalIntelligence, riskDecision }) {
  return requestJson('/generate-cam', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      company_name: companyName,
      financial_analysis: financialAnalysis || {},
      external_intelligence: externalIntelligence || {},
      risk_decision: riskDecision || {},
    }),
  })
}

export async function getDashboardSummary() {
  return requestJson('/dashboard/summary')
}

export async function getDashboardDeals() {
  return requestJson('/dashboard/deals')
}

export async function askCopilotQuestion({ companyData, question }) {
  return requestJson('/copilot/ask', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      company_data: companyData || {},
      question: question || '',
    }),
  })
}

export async function getPortfolioSummary() {
  return requestJson('/portfolio/summary')
}

export async function getPortfolioAlerts() {
  return requestJson('/portfolio/alerts')
}

export async function getPortfolioCompanies() {
  return requestJson('/portfolio/companies')
}

export async function getPortfolioHighRisk() {
  return requestJson('/portfolio/high-risk')
}
