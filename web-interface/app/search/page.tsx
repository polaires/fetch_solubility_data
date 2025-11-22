'use client'

import { useState } from 'react'
import Link from 'next/link'

interface SearchResult {
  filename: string
  part: string
  tableNum: number
  row: number
  data: Record<string, any>
  relevance: number
}

const COMMON_ELEMENTS = [
  { symbol: 'Na', name: 'Sodium' },
  { symbol: 'K', name: 'Potassium' },
  { symbol: 'Li', name: 'Lithium' },
  { symbol: 'Rb', name: 'Rubidium' },
  { symbol: 'Cs', name: 'Cesium' },
  { symbol: 'P', name: 'Phosphorus' },
  { symbol: 'H2O', name: 'Water' },
  { symbol: 'PO4', name: 'Phosphate' },
]

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const resultsPerPage = 50

  const handleSearch = async (query?: string) => {
    const searchTerm = query || searchQuery
    if (!searchTerm.trim()) return

    setLoading(true)
    setSearched(true)
    setCurrentPage(1)

    try {
      const searchResults: SearchResult[] = []

      // Search original tables
      const tablesRes = await fetch('/api/tables')
      const tablesData = await tablesRes.json()

      for (const table of tablesData.tables || []) {
        const tableRes = await fetch(`/api/tables/${encodeURIComponent(table.filename)}`)
        const tableData = await tableRes.json()

        if (!tableData.success) continue

        tableData.data.forEach((row: Record<string, any>, idx: number) => {
          const rowText = JSON.stringify(row).toLowerCase()
          const query = searchTerm.toLowerCase()

          if (rowText.includes(query)) {
            const occurrences = (rowText.match(new RegExp(query, 'g')) || []).length
            searchResults.push({
              filename: table.filename,
              part: table.part || 'Original',
              tableNum: table.tableNum,
              row: idx + 1,
              data: row,
              relevance: occurrences
            })
          }
        })
      }

      // Search filtered tables
      const filteredRes = await fetch('/api/filtered-tables')
      const filteredData = await filteredRes.json()

      for (const table of filteredData.tables || []) {
        const tableRes = await fetch(`/api/filtered-tables/${encodeURIComponent(table.filename)}`)
        const tableData = await tableRes.json()

        if (!tableData.success) continue

        tableData.data.forEach((row: Record<string, any>, idx: number) => {
          const rowText = JSON.stringify(row).toLowerCase()
          const query = searchTerm.toLowerCase()

          if (rowText.includes(query)) {
            const occurrences = (rowText.match(new RegExp(query, 'g')) || []).length
            searchResults.push({
              filename: table.filename,
              part: table.sds || 'Filtered',
              tableNum: table.tableNum,
              row: idx + 1,
              data: row,
              relevance: occurrences
            })
          }
        })
      }

      // Sort by relevance
      setResults(searchResults.sort((a, b) => b.relevance - a.relevance))
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleElementClick = (element: string) => {
    setSearchQuery(element)
    handleSearch(element)
  }

  const highlightText = (text: string, query: string) => {
    if (!query) return text
    const parts = String(text).split(new RegExp(`(${query})`, 'gi'))
    return (
      <span>
        {parts.map((part, i) =>
          part.toLowerCase() === query.toLowerCase() ? (
            <mark key={i} className="bg-yellow-200 px-1 rounded font-semibold">{part}</mark>
          ) : (
            part
          )
        )}
      </span>
    )
  }

  // Pagination
  const totalPages = Math.ceil(results.length / resultsPerPage)
  const startIdx = (currentPage - 1) * resultsPerPage
  const endIdx = startIdx + resultsPerPage
  const paginatedResults = results.slice(startIdx, endIdx)

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
            Search across all 642 tables for chemicals, compounds, or values
          </p>
        </div>
      </header>

      {/* Search Form */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="Search for elements, compounds, formulas, or values (e.g., 'Na', 'phosphate', '25°C')"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={() => handleSearch()}
              disabled={loading || !searchQuery.trim()}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Quick Element Filters */}
          <div className="mt-4">
            <p className="text-sm text-gray-700 font-medium mb-2">Quick element search:</p>
            <div className="flex flex-wrap gap-2">
              {COMMON_ELEMENTS.map((elem) => (
                <button
                  key={elem.symbol}
                  onClick={() => handleElementClick(elem.symbol)}
                  className="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 text-sm font-medium border border-blue-200"
                  title={elem.name}
                >
                  {elem.symbol}
                </button>
              ))}
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-500">
            <p><strong>Tips:</strong> Click an element button for quick search, or search for chemical names, formulas, temperatures, or any values. Results show individual matching rows.</p>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Searching 642 tables...</p>
          </div>
        )}

        {/* Results */}
        {!loading && searched && (
          <>
            <div className="mb-4 flex items-center justify-between">
              <div className="text-gray-600">
                Found <strong className="text-gray-900">{results.length}</strong> matching row{results.length !== 1 ? 's' : ''}
                {results.length > 0 && searchQuery && (
                  <span> for <strong className="text-blue-600">"{searchQuery}"</strong></span>
                )}
              </div>

              {/* Pagination Info */}
              {results.length > resultsPerPage && (
                <div className="text-sm text-gray-600">
                  Showing {startIdx + 1}-{Math.min(endIdx, results.length)} of {results.length}
                </div>
              )}
            </div>

            {results.length === 0 && (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <div className="text-gray-400 text-5xl mb-4">🔍</div>
                <h2 className="text-xl font-semibold text-gray-700 mb-2">No results found</h2>
                <p className="text-gray-500">
                  Try searching for common elements like "Na", "K", "Li", or compounds like "phosphate", "PO4"
                </p>
              </div>
            )}

            {/* Results Table */}
            {paginatedResults.length > 0 && (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Source</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Table</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Row</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Matches</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {paginatedResults.map((result, idx) => (
                        <tr key={`${result.filename}-${result.row}-${idx}`} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-gray-900 font-medium whitespace-nowrap">
                            {result.part}
                          </td>
                          <td className="px-4 py-3 text-gray-700 whitespace-nowrap">
                            #{result.tableNum.toString().padStart(3, '0')}
                          </td>
                          <td className="px-4 py-3 text-gray-500 font-mono text-xs">
                            {result.row}
                          </td>
                          <td className="px-4 py-3">
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 max-w-2xl">
                              {Object.entries(result.data).slice(0, 6).map(([key, value]) => (
                                <div key={key} className="flex flex-col">
                                  <span className="text-gray-500 text-xs truncate" title={key}>{key}</span>
                                  <span className="text-gray-900 font-mono text-xs">
                                    {highlightText(String(value || '—'), searchQuery)}
                                  </span>
                                </div>
                              ))}
                              {Object.keys(result.data).length > 6 && (
                                <div className="text-xs text-gray-400 flex items-center">
                                  +{Object.keys(result.data).length - 6} more
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {result.relevance}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <Link
                              href={`/table/${encodeURIComponent(result.filename)}`}
                              className="text-blue-600 hover:text-blue-700 text-xs font-medium"
                            >
                              View table →
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination Controls */}
                {totalPages > 1 && (
                  <div className="border-t px-4 py-3 flex items-center justify-between bg-gray-50">
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>

                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-700">
                        Page {currentPage} of {totalPages}
                      </span>
                    </div>

                    <button
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
