'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'

interface TableData {
  metadata: {
    filename: string
    part: string
    tableNum: number
    rows: number
    cols: number
    size: number
  }
  headers: string[]
  data: Record<string, any>[]
}

export default function TableView() {
  const params = useParams()
  const filename = decodeURIComponent(params.filename as string)

  const [tableData, setTableData] = useState<TableData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const rowsPerPage = 50

  useEffect(() => {
    // Try original tables first, then filtered tables
    const tryFetchTable = async () => {
      try {
        // Try original tables API
        let res = await fetch(`/api/tables/${encodeURIComponent(filename)}`)
        let data = await res.json()

        // If not found, try filtered tables API
        if (!data.success) {
          res = await fetch(`/api/filtered-tables/${encodeURIComponent(filename)}`)
          data = await res.json()
        }

        if (data.success) {
          setTableData(data)
        } else {
          setError(data.error || 'Failed to load table')
        }
        setLoading(false)
      } catch (err: any) {
        setError(err.message)
        setLoading(false)
      }
    }

    tryFetchTable()
  }, [filename])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading table data...</p>
        </div>
      </div>
    )
  }

  if (error || !tableData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-5xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Table</h2>
          <p className="text-gray-600 mb-6">{error || 'Unknown error occurred'}</p>
          <Link
            href="/"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            ← Back to Tables List
          </Link>
        </div>
      </div>
    )
  }

  const { metadata, headers, data } = tableData

  // Filter data based on search
  const filteredData = data.filter(row => {
    if (!searchTerm) return true
    return Object.values(row).some(val =>
      String(val).toLowerCase().includes(searchTerm.toLowerCase())
    )
  })

  // Pagination
  const totalPages = Math.ceil(filteredData.length / rowsPerPage)
  const startIdx = (currentPage - 1) * rowsPerPage
  const endIdx = startIdx + rowsPerPage
  const paginatedData = filteredData.slice(startIdx, endIdx)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <Link
                href="/"
                className="text-blue-600 hover:text-blue-700 text-sm font-medium mb-2 inline-block"
              >
                ← Back to Tables
              </Link>
              <h1 className="text-2xl font-bold text-gray-900">
                {metadata.part} - Table {metadata.tableNum.toString().padStart(3, '0')}
              </h1>
              <p className="text-sm text-gray-600 mt-1">{metadata.filename}</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-600">
                {metadata.rows} rows × {metadata.cols} columns
              </div>
              <div className="text-xs text-gray-500">
                {(metadata.size / 1024).toFixed(1)} KB
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Search & Pagination Controls */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            {/* Search */}
            <div className="flex-1 w-full md:max-w-md">
              <input
                type="text"
                placeholder="Search in table..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value)
                  setCurrentPage(1)
                }}
              />
            </div>

            {/* Pagination Info */}
            <div className="text-sm text-gray-600">
              Showing {startIdx + 1}-{Math.min(endIdx, filteredData.length)} of {filteredData.length} rows
              {searchTerm && ` (filtered from ${data.length})`}
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b sticky top-[88px]">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    #
                  </th>
                  {headers.map((header, idx) => (
                    <th
                      key={idx}
                      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {paginatedData.map((row, rowIdx) => (
                  <tr key={rowIdx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-500 font-mono text-xs">
                      {startIdx + rowIdx + 1}
                    </td>
                    {headers.map((header, colIdx) => (
                      <td key={colIdx} className="px-4 py-3 text-gray-900 whitespace-nowrap">
                        {row[header] || '—'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="border-t px-4 py-3 flex items-center justify-between">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>

              <div className="flex items-center gap-2">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  let pageNum
                  if (totalPages <= 5) {
                    pageNum = i + 1
                  } else if (currentPage <= 3) {
                    pageNum = i + 1
                  } else if (currentPage >= totalPages - 2) {
                    pageNum = totalPages - 4 + i
                  } else {
                    pageNum = currentPage - 2 + i
                  }

                  return (
                    <button
                      key={i}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`px-3 py-1 text-sm rounded ${
                        currentPage === pageNum
                          ? 'bg-blue-600 text-white'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      {pageNum}
                    </button>
                  )
                })}
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

        {/* Empty State */}
        {filteredData.length === 0 && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <p className="text-gray-500">No rows match your search criteria.</p>
          </div>
        )}
      </main>
    </div>
  )
}
