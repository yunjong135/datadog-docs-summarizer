import React, { useState } from 'react'

export default function SearchBar({ onSearch, isLoading }) {
  const [value, setValue] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    const trimmed = value.trim()
    if (!trimmed || isLoading) return
    onSearch(trimmed)
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 w-full max-w-2xl mx-auto">
      <div className="relative flex-1">
        <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-gray-400">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
          </svg>
        </div>
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="예: APM tracing, Log management, Monitors..."
          disabled={isLoading}
          className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300
                     focus:outline-none focus:ring-2 focus:ring-dd-purple focus:border-transparent
                     disabled:bg-gray-100 disabled:cursor-not-allowed
                     text-gray-900 placeholder-gray-400 bg-white shadow-sm"
        />
      </div>
      <button
        type="submit"
        disabled={isLoading || !value.trim()}
        className="btn-primary flex items-center gap-2 whitespace-nowrap"
      >
        {isLoading ? (
          <><span className="spinner" />검색 중...</>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
            </svg>
            검색
          </>
        )}
      </button>
    </form>
  )
}
