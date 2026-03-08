const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

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
