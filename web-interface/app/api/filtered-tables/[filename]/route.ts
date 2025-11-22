import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import Papa from 'papaparse'

export async function GET(
  request: Request,
  { params }: { params: { filename: string } }
) {
  try {
    const filename = params.filename
    const dataDir = path.join(process.cwd(), 'public', 'filtered_data')
    const filePath = path.join(dataDir, filename)

    // Check if file exists
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({
        error: 'Table not found',
        success: false
      }, { status: 404 })
    }

    // Read and parse CSV
    const csvContent = fs.readFileSync(filePath, 'utf-8')

    const parsed = Papa.parse(csvContent, {
      header: true,
      skipEmptyLines: true
    })

    if (parsed.errors.length > 0) {
      console.error('CSV parsing errors:', parsed.errors)
    }

    return NextResponse.json({
      success: true,
      filename,
      headers: parsed.meta.fields || [],
      data: parsed.data,
      source: 'filtered_booklet'
    })
  } catch (error) {
    console.error('Error reading filtered table:', error)
    return NextResponse.json({
      error: 'Failed to read table',
      success: false
    }, { status: 500 })
  }
}
