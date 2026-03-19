import React from 'react'

function ResultItem({ result, isSelected, onClick, isSummarizing }) {
  return (
    <li
      className={`result-item group${isSelected ? ' selected' : ''}`}
      onClick={() => !isSummarizing && onClick(result)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && !isSummarizing && onClick(result)}
    >
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <h3 className={`font-medium text-sm leading-snug mb-1 truncate
            ${isSelected ? 'text-dd-purple' : 'text-gray-900 group-hover:text-dd-purple'}`}>
            {result.title}
          </h3>
          <p className="text-xs text-gray-400 truncate mb-1.5">{result.url}</p>
          {result.excerpt && (
            <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed">{result.excerpt}</p>
          )}
        </div>
        <div className="flex-shrink-0 mt-0.5">
          {isSelected && isSummarizing ? (
            <span className="spinner text-dd-purple" />
          ) : (
            <svg className={`w-4 h-4 ${isSelected ? 'text-dd-purple' : 'text-gray-300 group-hover:text-dd-purple'}`}
              fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          )}
        </div>
      </div>
    </li>
  )
}

export default function ResultList({ results, selectedDoc, onSelect, isSummarizing }) {
  if (!results) return null
  if (results.length === 0) {
    return (
      <div className="card p-8 text-center">
        <div className="text-4xl mb-3">🔍</div>
        <p className="text-gray-500 font-medium">검색 결과가 없습니다</p>
        <p className="text-gray-400 text-sm mt-1">다른 키워드로 시도해보세요</p>
      </div>
    )
  }
  return (
    <div className="card overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">검색 결과</span>
        <span className="text-xs text-gray-400 bg-white border border-gray-200 rounded-full px-2 py-0.5">
          {results.length}건
        </span>
      </div>
      <ul className="divide-y divide-gray-100">
        {results.map((result, idx) => (
          <ResultItem
            key={result.url ?? idx}
            result={result}
            isSelected={selectedDoc?.url === result.url}
            onClick={onSelect}
            isSummarizing={isSummarizing}
          />
        ))}
      </ul>
    </div>
  )
}
