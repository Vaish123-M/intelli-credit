const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export function getApiBaseUrl() {
  return API_BASE_URL
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
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, options)
    return await parseResponse(response)
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error('Could not connect to backend API. Please ensure the backend server is running on port 8000.')
    }
    throw error
  }
}

export async function uploadFiles(files) {
  const formData = new FormData()
  files.forEach((file) => formData.append('files', file))

  return requestJson('/upload', {
    method: 'POST',
    body: formData,
  })
}

export async function runAnalysis() {
  const payload = await requestJson('/analyze', {
    method: 'POST',
  })

  if (payload.analysis) {
    return payload
  }

  const { extracted_data: extractedData, ...analysis } = payload
  return { analysis, extracted_data: extractedData || [] }
}

export async function getResults() {
  return requestJson('/results')
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
