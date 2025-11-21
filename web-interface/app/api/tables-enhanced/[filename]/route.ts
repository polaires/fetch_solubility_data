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

    // Security check
    if (filename.includes('..') || filename.includes('/')) {
      return NextResponse.json({
        error: 'Invalid filename'
      }, { status: 400 })
    }

    // Try multiple data locations
    const possibleDirs = [
      path.join(process.cwd(), '..', 'output', '02_cleaned_enhanced'),
      path.join(process.cwd(), 'public', 'data_enhanced'),
    ]

    let dataDir = ''
    for (const dir of possibleDirs) {
      const testPath = path.join(dir, filename)
      if (fs.existsSync(testPath)) {
        dataDir = dir
        break
      }
    }

    if (!dataDir) {
      return NextResponse.json({
        error: 'Enhanced table not found'
      }, { status: 404 })
    }

    const filePath = path.join(dataDir, filename)

    // Read CSV
    const content = fs.readFileSync(filePath, 'utf-8')
    const parsed = Papa.parse(content, {
      header: true,
      skipEmptyLines: true,
      dynamicTyping: false,
    })

    // Load metadata
    const metadataPath = path.join(dataDir, 'metadata', `${filename.replace('.csv', '_metadata.json')}`)
    let metadata = null
    let columnMetadata = null

    if (fs.existsSync(metadataPath)) {
      const metaContent = fs.readFileSync(metadataPath, 'utf-8')
      metadata = JSON.parse(metaContent)

      // Extract useful column metadata
      if (metadata.column_analysis) {
        columnMetadata = {
          types: metadata.column_analysis.types_detected,
          standardNames: metadata.column_analysis.standard_names,
          summary: metadata.column_analysis.summary,
        }
      }
    }

    // Parse filename for metadata
    const match = filename.match(/SDS-31_(Part\d+)_table_(\d+)\.csv/)
    const part = match ? match[1] : 'Unknown'
    const tableNum = match ? parseInt(match[2], 10) : 0

    const stats = fs.statSync(filePath)

    return NextResponse.json({
      success: true,
      metadata: {
        filename,
        part,
        tableNum,
        rows: parsed.data.length,
        cols: parsed.meta.fields?.length || 0,
        size: stats.size,
        // Enhanced metadata
        chemicalSystem: metadata?.chemical_system || 'Unknown',
        systemConfidence: metadata?.system_confidence || 'none',
        phasesFound: metadata?.phase_extraction?.phases_found || [],
        phaseColumnsAdded: metadata?.phase_extraction?.phase_columns_added || 0,
      },
      headers: parsed.meta.fields || [],
      data: parsed.data,
      columnMetadata,
      errors: parsed.errors.length > 0 ? parsed.errors : null
    })

  } catch (error: any) {
    console.error('Error reading enhanced table:', error)
    return NextResponse.json({
      error: error.message || 'Failed to load enhanced table'
    }, { status: 500 })
  }
}
