import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET() {
  try {
    // Path to cleaned data (relative to project root)
    const dataDir = path.join(process.cwd(), '..', 'output', '02_cleaned')

    // Check if directory exists
    if (!fs.existsSync(dataDir)) {
      return NextResponse.json({
        error: 'Data directory not found',
        tables: []
      })
    }

    // Read all CSV files
    const files = fs.readdirSync(dataDir)
      .filter(file => file.endsWith('.csv') && !file.includes('manifest'))
      .sort()

    // Parse file information
    const tables = files.map(filename => {
      const filePath = path.join(dataDir, filename)
      const stats = fs.statSync(filePath)

      // Parse filename: SDS-31_Part1_table_001.csv
      const match = filename.match(/SDS-31_(Part\d+)_table_(\d+)\.csv/)
      const part = match ? match[1] : 'Unknown'
      const tableNum = match ? parseInt(match[2], 10) : 0

      // Count rows and columns
      const content = fs.readFileSync(filePath, 'utf-8')
      const lines = content.trim().split('\n')
      const rows = lines.length - 1 // Subtract header
      const cols = lines.length > 0 ? lines[0].split(',').length : 0

      return {
        filename,
        part,
        tableNum,
        rows,
        cols,
        size: stats.size,
        hasData: rows > 0
      }
    })

    return NextResponse.json({
      success: true,
      count: tables.length,
      tables
    })

  } catch (error: any) {
    console.error('Error reading tables:', error)
    return NextResponse.json({
      error: error.message || 'Failed to load tables',
      tables: []
    }, { status: 500 })
  }
}
