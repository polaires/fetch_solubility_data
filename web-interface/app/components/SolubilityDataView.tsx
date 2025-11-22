'use client'

interface SolubilityDataViewProps {
  data: Record<string, any>[]
  headers: string[]
  metadata: {
    filename: string
    part: string
    tableNum: number
  }
}

export function SolubilityDataView({ data, headers, metadata }: SolubilityDataViewProps) {
  // Detect column types based on content
  const detectColumnType = (header: string, sampleValues: any[]) => {
    const sampleStr = sampleValues.join(' ').toLowerCase()

    if (sampleStr.includes('mass%') || header.includes('mass') || sampleStr.match(/\d+\.\d+%/)) {
      return 'mass_percent'
    }
    if (sampleStr.includes('mol/kg') || sampleStr.includes('molality')) {
      return 'molality'
    }
    if (sampleStr.includes('°c') || sampleStr.includes('temp')) {
      return 'temperature'
    }
    if (sampleStr.includes('ph')) {
      return 'pH'
    }
    if (sampleStr.match(/\b[a-f]\b/i) || sampleStr.match(/\b[ivx]+\b/i)) {
      return 'phase'
    }
    if (sampleValues.every(v => !isNaN(parseFloat(String(v).replace(/,/g, '.'))) || v === '' || v === '----')) {
      return 'numeric'
    }
    return 'text'
  }

  // Get sample values for each column
  const columnTypes = headers.map(header => {
    const sampleValues = data.slice(0, 10).map(row => row[header])
    return {
      header,
      type: detectColumnType(header, sampleValues)
    }
  })

  // Format value based on type
  const formatValue = (value: any, type: string) => {
    if (value === '' || value === '----' || value === null || value === undefined) {
      return '—'
    }

    const strValue = String(value)

    switch (type) {
      case 'mass_percent':
        return strValue + (strValue.includes('%') ? '' : ' mass%')
      case 'molality':
        return strValue + (strValue.includes('mol') ? '' : ' mol/kg')
      case 'temperature':
        return strValue + (strValue.includes('°') ? '' : ' °C')
      case 'numeric':
        // Clean up numeric value
        return strValue.replace(/,/g, '.')
      default:
        return strValue
    }
  }

  return (
    <div className="space-y-4">
      {/* Data Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Row
                </th>
                {columnTypes.map((col, idx) => (
                  <th
                    key={idx}
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                  >
                    <div className="flex flex-col">
                      <span>{col.header}</span>
                      <span className="text-[10px] text-gray-400 font-normal normal-case">
                        {col.type === 'mass_percent' && 'Mass %'}
                        {col.type === 'molality' && 'mol/kg'}
                        {col.type === 'temperature' && '°C'}
                        {col.type === 'pH' && 'pH'}
                        {col.type === 'phase' && 'Phase'}
                        {col.type === 'numeric' && 'Value'}
                        {col.type === 'text' && 'Text'}
                      </span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.map((row, rowIdx) => (
                <tr key={rowIdx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-500 font-mono text-xs">
                    {rowIdx + 1}
                  </td>
                  {columnTypes.map((col, colIdx) => (
                    <td key={colIdx} className="px-4 py-3 text-gray-900 whitespace-nowrap">
                      <span className={
                        col.type === 'phase' ? 'font-bold text-blue-600' :
                        col.type === 'temperature' ? 'text-orange-600' :
                        col.type === 'pH' ? 'text-green-600' :
                        'text-gray-900'
                      }>
                        {formatValue(row[col.header], col.type)}
                      </span>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Info Panel */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
        <h3 className="font-semibold text-blue-900 mb-2">About this data:</h3>
        <ul className="text-blue-800 space-y-1">
          <li>• <strong>Source:</strong> SDS-31 (IUPAC Solubility Data Series) - Alkali Metal Orthophosphates</li>
          <li>• <strong>Data Type:</strong> Binary/Ternary aqueous solubility systems</li>
          <li>• <strong>Phase Labels:</strong> A, B, C, etc. indicate different solid phases in equilibrium</li>
          <li>• <strong>Columns:</strong> May include concentration (mass%, mol/kg), temperature, pH, and solid phase information</li>
        </ul>
      </div>
    </div>
  )
}
