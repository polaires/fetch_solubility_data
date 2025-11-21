'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface TableInfo {
  filename: string
  part: string
  tableNum: number
  rows: number
  cols: number
  hasData: boolean
}

export default function Home() {
  const [tables, setTables] = useState<TableInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterPart, setFilterPart] = useState<string>('all')

  useEffect(() => {
    fetch('/api/tables')
      .then(res => res.json())
      .then(data => {
        setTables(data.tables || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Error loading tables:', err)
        setLoading(false)
      })
  }, [])

  // Get unique parts for filter
  const parts = Array.from(new Set(tables.map(t => t.part))).sort()

  // Filter tables
  const filteredTables = tables.filter(table => {
    const matchesSearch = table.filename.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesPart = filterPart === 'all' || table.part === filterPart
    return matchesSearch && matchesPart
  })

  // Group by part
  const tablesByPart = filteredTables.reduce((acc, table) => {
    if (!acc[table.part]) acc[table.part] = []
    acc[table.part].push(table)
    return acc
  }, {} as Record<string, TableInfo[]>)

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading tables...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Solubility Data Viewer
          </h1>
          <p className="mt-2 text-gray-600">
            Browse and examine extracted solubility data from SDS-31 PDFs
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Total Tables</div>
            <div className="text-3xl font-bold text-blue-600">{tables.length}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">PDF Parts</div>
            <div className="text-3xl font-bold text-green-600">{parts.length}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600">Filtered Results</div>
            <div className="text-3xl font-bold text-purple-600">{filteredTables.length}</div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Tables
              </label>
              <input
                type="text"
                placeholder="Filter by filename..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            {/* Part Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by PDF Part
              </label>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={filterPart}
                onChange={(e) => setFilterPart(e.target.value)}
              >
                <option value="all">All Parts</option>
                {parts.map(part => (
                  <option key={part} value={part}>{part}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Tables List */}
        {Object.keys(tablesByPart).length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500">No tables found matching your criteria.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(tablesByPart)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([part, partTables]) => (
                <div key={part} className="bg-white rounded-lg shadow overflow-hidden">
                  <div className="bg-blue-50 px-6 py-3 border-b">
                    <h2 className="text-lg font-semibold text-gray-900">
                      {part} ({partTables.length} tables)
                    </h2>
                  </div>
                  <div className="divide-y">
                    {partTables
                      .sort((a, b) => a.tableNum - b.tableNum)
                      .map((table) => (
                        <Link
                          key={table.filename}
                          href={`/table/${encodeURIComponent(table.filename)}`}
                          className="block px-6 py-4 hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-medium text-gray-900">
                                Table {table.tableNum.toString().padStart(3, '0')}
                              </div>
                              <div className="text-sm text-gray-500">
                                {table.filename}
                              </div>
                            </div>
                            <div className="flex items-center gap-4 text-sm">
                              <div className="text-gray-600">
                                {table.rows} rows × {table.cols} cols
                              </div>
                              <svg
                                className="w-5 h-5 text-gray-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M9 5l7 7-7 7"
                                />
                              </svg>
                            </div>
                          </div>
                        </Link>
                      ))}
                  </div>
                </div>
              ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-gray-600 text-sm">
          <p>Solubility Data Examination Interface • For development and testing purposes</p>
        </div>
      </footer>
    </div>
  )
}
