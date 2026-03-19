import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'

export default function SummaryCard({ doc, summary, isLoading }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(summary)
    } catch {
      const ta = document.createElement('textarea')
      ta.value = summary
      ta.style.position = 'fixed'
      ta.style.opacity = '0'
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (!doc && !isLoading) {
    return (
      <div className="card p-10 flex flex-col items-center justify-center text-center h-full min-h-[300px]">
        <div className="w-16 h-16 rounded-full bg-dd-purple-bg flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-dd-purple" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p className="text-gray-500 font-medium">문서를 선택하면 한글 요약이 표시됩니다</p>
        <p className="text-gray-400 text-sm mt-1">왼쪽 검색 결과에서 항목을 클릭하세요</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="card p-10 flex flex-col items-center justify-center h-full min-h-[300px]">
        <span className="spinner spinner-lg text-dd-purple mb-4" />
        <p className="text-gray-500 font-medium">문서 분석 및 요약 중...</p>
        <p className="text-gray-400 text-sm mt-1">잠시만 기다려 주세요</p>
      </div>
    )
  }

  return (
    <div className="card overflow-hidden flex flex-col">
      <div className="px-5 py-4 border-b border-gray-100 bg-gradient-to-r from-dd-purple to-dd-purple-light">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <span className="text-xs font-medium text-purple-200 uppercase tracking-wide">요약</span>
            <h2 className="text-white font-semibold text-base leading-snug line-clamp-2 mt-1">
              {doc.title}
            </h2>
          </div>
          <button
            onClick={handleCopy}
            className="flex-shrink-0 flex items-center gap-1.5 text-xs text-purple-200 hover:text-white
                       bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-md transition-colors duration-150"
          >
            {copied ? (
              <><svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
              </svg>복사됨</>
            ) : (
              <><svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>복사</>
            )}
          </button>
        </div>
        <a href={doc.url} target="_blank" rel="noopener noreferrer"
          className="mt-2 inline-flex items-center gap-1 text-xs text-purple-200 hover:text-white underline underline-offset-2">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          원본 문서 보기
        </a>
      </div>
      <div className="p-5 flex-1 overflow-y-auto">
        <div className="markdown-body">
          <ReactMarkdown>{summary}</ReactMarkdown>
        </div>
      </div>
    </div>
  )
}
