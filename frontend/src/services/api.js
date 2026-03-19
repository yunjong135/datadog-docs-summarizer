const BASE_URL = import.meta.env.VITE_API_URL ?? ''

export async function searchDocs(query) {
  const response = await fetch(`${BASE_URL}/api/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail ?? `검색 실패: ${response.status}`)
  }
  const data = await response.json()
  return data.results
}

export async function summarizeDoc(url) {
  const response = await fetch(`${BASE_URL}/api/summarize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail ?? `요약 실패: ${response.status}`)
  }
  return response.json()
}
