import React, { useState } from 'react'
import SearchBar from './components/SearchBar.jsx'
import ResultList from './components/ResultList.jsx'
import SummaryCard from './components/SummaryCard.jsx'
import { searchDocs, summarizeDoc } from './services/api.js'

export default function App() {
  const [searchQuery, setSearchQuery]     = useState('')
  const [searchResults, setSearchResults] = useState(null)
  const [selectedDoc, setSelectedDoc]     = useState(null)
  const [summary, setSummary]             = useState('')
  const [isSearching, setIsSearching]     = useState(false)
  const [isSummarizing, setIsSummarizing] = useState(false)
  const [error, setError]                 = useState(null)

  const handleSearch = async (query) => {
    setSearchQuery(query)
    setSearchResults(null)
    setSelectedDoc(null)
    setSummary('')
    setError(null)
    setIsSearching(true)
    try {
      const results = await searchDocs(query)
      setSearchResults(results)
    } catch (err) {
      setError({ type: 'search', message: err.message })
    } finally {
      setIsSearching(false)
    }
  }

  const handleSelectDoc = async (doc) => {
    if (isSummarizing || selectedDoc?.url === doc.url) return
    setSelectedDoc(doc)
    setSummary('')
    setError(null)
    setIsSummarizing(true)
    try {
      const data = await summarizeDoc(doc.url)
      setSummary(data.summary)
    } catch (err) {
      setError({ type: 'summarize', message: err.message })
    } finally {
      setIsSummarizing(false)
    }
  }

  const hasResults = searchResults !== null

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            <div className="flex items-center gap-3 flex-shrink-0">
              <div className="w-9 h-9 rounded-lg bg-dd-purple flex items-center justify-center shadow-sm">
                <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/>
                </svg>
              </div>
              <div>
                <h1 className="text-base font-bold text-gray-900 leading-tight">Datadog Docs</h1>
                <p className="text-xs text-dd-purple font-medium">한글 요약 서비스</p>
              </div>
            </div>
            <div className="flex-1">
              <SearchBar onSearch={handleSearch} isLoading={isSearching} />
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 sm:px-6 py-6">
        {error && (
          <div className="mb-4 flex items-start gap-3 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
            <svg className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-medium text-red-700">
                {error.type === 'search' ? '검색 오류' : '요약 오류'}
              </p>
              <p className="text-sm text-red-600 mt-0.5">{error.message}</p>
            </div>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-red-600">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {!hasResults && !isSearching && (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-20 h-20 rounded-2xl bg-dd-purple-bg flex items-center justify-center mb-6">
              <svg className="w-10 h-10 text-dd-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
              </svg>
            </div>
            <h2 className="text-xl font-bold text-gray-800 mb-2">Datadog 문서를 검색하세요</h2>
            <p className="text-gray-500 max-w-md">
              원하는 Datadog 기능이나 주제를 검색하면 공식 문서를 찾아 한글로 요약해 드립니다.
            </p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center">
              {['APM Tracing', 'Log Management', 'Synthetic Monitoring', 'Dashboards', 'Alerts & Monitors'].map((tag) => (
                <button key={tag} onClick={() => handleSearch(tag)}
                  className="text-sm text-dd-purple bg-dd-purple-bg hover:bg-purple-100
                             border border-purple-200 px-3 py-1.5 rounded-full transition-colors duration-100">
                  {tag}
                </button>
              ))}
            </div>
          </div>
        )}

        {isSearching && (
          <div className="flex flex-col items-center justify-center py-20">
            <span className="spinner spinner-lg text-dd-purple mb-4" />
            <p className="text-gray-500">&quot;{searchQuery}&quot; 검색 중...</p>
          </div>
        )}

        {hasResults && !isSearching && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="lg:max-h-[calc(100vh-160px)] lg:overflow-y-auto">
              <ResultList
                results={searchResults}
                selectedDoc={selectedDoc}
                onSelect={handleSelectDoc}
                isSummarizing={isSummarizing}
              />
            </div>
            <div className="lg:max-h-[calc(100vh-160px)] lg:overflow-y-auto lg:sticky lg:top-[88px]">
              <SummaryCard doc={selectedDoc} summary={summary} isLoading={isSummarizing} />
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-gray-200 bg-white mt-auto">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <p className="text-xs text-gray-400">Powered by Datadog Official Docs + Claude AI</p>
          <a href="https://docs.datadoghq.com" target="_blank" rel="noopener noreferrer"
            className="text-xs text-dd-purple hover:text-dd-purple-dark transition-colors">
            docs.datadoghq.com
          </a>
        </div>
      </footer>
    </div>
  )
}
