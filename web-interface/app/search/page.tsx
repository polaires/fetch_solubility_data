'use client'

import { useState } from 'react'
import Link from 'next/link'

interface SearchResult {
  filename: string
  part: string
  tableNum: number
  matches: Array<{
    row: number
    data: Record<string, any>
    relevance: number
  }>
}

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setLoading(true)
    setSearched(true)

    try {
      // Get all tables
      const tablesRes = await fetch('/api/tables')
      const tablesData = await tablesRes.json()

      const searchResults: SearchResult[] = []

      // Search through each table
      for (const table of tablesData.tables || []) {
        const tableRes = await fetch(`/api/tables/${encodeURIComponent(table.filename)}`)
        const tableData = await tableRes.json()

        if (!tableData.success) continue

        const matches: Array<{row: number, data: Record<string, any>, relevance: number}> = []

        // Search through rows
        tableData.data.forEach((row: Record<string, any>, idx: number) => {
          const rowText = JSON.stringify(row).toLowerCase()
          const query = searchQuery.toLowerCase()

          if (rowText.includes(query)) {
            // Calculate relevance (simple: count occurrences)
            const occurrences = (rowText.match(new RegExp(query, 'g')) || []).length
            matches.push({
              row: idx + 1,
              data: row,
              relevance: occurrences
            })
          }
        })

        if (matches.length > 0) {
          searchResults.push({
            filename: table.filename,
            part: table.part,
            tableNum: table.tableNum,
            matches: matches.sort((a, b) => b.relevance - a.relevance).slice(0, 5) // Top 5 matches per table
          })
        }
      }

      setResults(searchResults.sort((a, b) =>
        b.matches.reduce((sum, m) => sum + m.relevance, 0) -
        a.matches.reduce((sum, m) => sum + m.relevance, 0)
      ))
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setLoading(false)
    }
  }

  const highlightText = (text: string, query: string) => {
    if (!query) return text
    const parts = String(text).split(new RegExp(`(${query})`, 'gi'))
    return (
      <span>
        {parts.map((part, i) =>
          part.toLowerCase() === query.toLowerCase() ? (
            <mark key={i} className="bg-yellow-200 px-1 rounded">{part}</mark>
          ) : (
            part
          )
        )}
      </span>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <Link
            href="/"
            className="text-blue-600 hover:text-blue-700 text-sm font-medium mb-2 inline-block"
          >
            ← Back to Tables
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Search Solubility Data</h1>
          <p className="text-gray-600 mt-1">
            Search across all 338 tables for chemicals, compounds, or values
          </p>
        </div>
      </header>

      {/* Search Form */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="Search for chemical names, formulas, values, etc. (e.g., 'Na3PO4', 'phosphate', '25°C')"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              disabled={loading || !searchQuery.trim()}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>

          <div className="mt-4 text-sm text-gray-500">
            <p><strong>Tips:</strong> Search for chemical names (Na3PO4), formulas (H2O), temperatures (25°C), or any numeric values</p>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Searching {338} tables...</p>
          </div>
        )}

        {/* Results */}
        {!loading && searched && (
          <>
            <div className="mb-4 text-gray-600">
              Found <strong>{results.length}</strong> tables with matches
              {results.length > 0 && (
                <span> containing <strong>{results.reduce((sum, r) => sum + r.matches.length, 0)}</strong> total matches</span>
              )}
            </div>

            {results.length === 0 && (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <div className="text-gray-400 text-5xl mb-4">🔍</div>
                <h2 className="text-xl font-semibold text-gray-700 mb-2">No results found</h2>
                <p className="text-gray-500">
                  Try searching for common chemicals like "phosphate", "Na", "KH2PO4", or numeric values
                </p>
              </div>
            )}

            {results.map((result) => (
              <div key={result.filename} className="bg-white rounded-lg shadow mb-4">
                <div className="p-4 border-b bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {result.part} - Table {result.tableNum.toString().padStart(3, '0')}
                      </h3>
                      <p className="text-sm text-gray-600">{result.filename}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-blue-600">
                        {result.matches.length} match{result.matches.length !== 1 ? 'es' : ''}
                      </div>
                      <Link
                        href={`/table/${encodeURIComponent(result.filename)}`}
                        className="text-sm text-blue-600 hover:text-blue-700"
                      >
                        View full table →
                      </Link>
                    </div>
                  </div>
                </div>

                <div className="p-4">
                  {result.matches.map((match, idx) => (
                    <div key={idx} className="mb-4 last:mb-0 pb-4 last:pb-0 border-b last:border-b-0">
                      <div className="text-xs text-gray-500 mb-2">Row {match.row}</div>
                      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 text-sm">
                        {Object.entries(match.data).map(([key, value]) => (
                          <div key={key} className="flex flex-col">
                            <span className="text-gray-500 text-xs">Column {key}</span>
                            <span className="text-gray-900 font-mono">
                              {highlightText(String(value || '—'), searchQuery)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </>
        )}
      </main>
    </div>
  )
}
