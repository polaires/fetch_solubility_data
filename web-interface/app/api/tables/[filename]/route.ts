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

    // Security check: ensure filename doesn't contain path traversal
    if (filename.includes('..') || filename.includes('/')) {
      return NextResponse.json({
        error: 'Invalid filename'
      }, { status: 400 })
    }

    // Try multiple data locations (for Vercel deployment and local dev)
    const possibleDirs = [
      path.join(process.cwd(), 'public', 'data'),                      // Vercel deployment
      path.join(process.cwd(), '..', 'output', '02_cleaned', 'cleaned_data'), // Local dev (nested)
      path.join(process.cwd(), '..', 'output', '02_cleaned'),          // Local dev (flat)
    ]

    let filePath = ''
    for (const dir of possibleDirs) {
      const testPath = path.join(dir, filename)
      if (fs.existsSync(testPath)) {
        filePath = testPath
        break
      }
    }

    // Check if file exists
    if (!filePath || !fs.existsSync(filePath)) {
      return NextResponse.json({
        error: 'Table not found'
      }, { status: 404 })
    }

    // Read and parse CSV
    const content = fs.readFileSync(filePath, 'utf-8')
    const parsed = Papa.parse(content, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: false, // Keep as strings to preserve formatting
    })

    // Get metadata
    const stats = fs.statSync(filePath)

    // Parse filename for metadata
    const match = filename.match(/SDS-31_(Part\d+)_table_(\d+)\.csv/)
    const part = match ? match[1] : 'Unknown'
    const tableNum = match ? parseInt(match[2], 10) : 0

    return NextResponse.json({
      success: true,
      metadata: {
        filename,
        part,
        tableNum,
        rows: parsed.data.length,
        cols: parsed.meta.fields?.length || 0,
        size: stats.size,
      },
      headers: parsed.meta.fields || [],
      data: parsed.data,
      errors: parsed.errors.length > 0 ? parsed.errors : null
    })

  } catch (error: any) {
    console.error('Error reading table:', error)
    return NextResponse.json({
      error: error.message || 'Failed to load table'
    }, { status: 500 })
  }
}
