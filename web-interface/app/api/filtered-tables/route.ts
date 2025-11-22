import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import Papa from 'papaparse'

export async function GET() {
  try {
    const dataDir = path.join(process.cwd(), 'public', 'filtered_data')

    // Check if directory exists
    if (!fs.existsSync(dataDir)) {
      return NextResponse.json({
        error: 'Filtered data directory not found',
        success: false
      })
    }

    // Get all CSV files
    const files = fs.readdirSync(dataDir)
      .filter(file => file.endsWith('.csv') && !file.startsWith('_'))
      .sort()

    // Extract metadata from filenames (SDS-XX_table_YYY.csv)
    const tables = files.map(filename => {
      const match = filename.match(/SDS-(\d+)_table_(\d+)\.csv/)
      if (!match) {
        return {
          filename,
          sds: 'Unknown',
          tableNum: 0
        }
      }

      const [_, sdsNum, tableNum] = match

      // Get file stats for row count (quick approximation)
      const filePath = path.join(dataDir, filename)
      const content = fs.readFileSync(filePath, 'utf-8')
      const lines = content.split('\n').filter(line => line.trim())
      const rows = lines.length - 1 // Subtract header row

      return {
        filename,
        sds: `SDS-${sdsNum}`,
        tableNum: parseInt(tableNum),
        rows,
        source: 'filtered_booklet'
      }
    })

    return NextResponse.json({
      success: true,
      count: tables.length,
      tables
    })
  } catch (error) {
    console.error('Error listing filtered tables:', error)
    return NextResponse.json({
      error: 'Failed to list filtered tables',
      success: false
    }, { status: 500 })
  }
}
