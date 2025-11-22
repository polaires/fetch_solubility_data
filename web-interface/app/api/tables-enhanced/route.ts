import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET() {
  try {
    // Try multiple data locations
    const possibleDirs = [
      path.join(process.cwd(), '..', 'output', '02_cleaned_enhanced'),
      path.join(process.cwd(), 'public', 'data_enhanced'),
    ]

    let dataDir = ''
    for (const dir of possibleDirs) {
      if (fs.existsSync(dir)) {
        dataDir = dir
        break
      }
    }

    if (!dataDir || !fs.existsSync(dataDir)) {
      return NextResponse.json({
        error: 'Enhanced data directory not found',
        tables: []
      })
    }

    // Load summary
    const summaryPath = path.join(dataDir, 'enhanced_cleaning_summary.json')
    let summary = {}
    if (fs.existsSync(summaryPath)) {
      summary = JSON.parse(fs.readFileSync(summaryPath, 'utf-8'))
    }

    // Read all CSV files
    const files = fs.readdirSync(dataDir)
      .filter(file => file.endsWith('.csv'))
      .sort()

    // Load metadata for each file
    const metadataDir = path.join(dataDir, 'metadata')
    const tables = files.map(filename => {
      const filePath = path.join(dataDir, filename)
      const stats = fs.statSync(filePath)

      // Load metadata if exists
      const metadataPath = path.join(metadataDir, `${filename.replace('.csv', '_metadata.json')}`)
      let metadata = null
      if (fs.existsSync(metadataPath)) {
        metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf-8'))
      }

      // Parse filename
      const match = filename.match(/SDS-31_(Part\d+)_table_(\d+)\.csv/)
      const part = match ? match[1] : 'Unknown'
      const tableNum = match ? parseInt(match[2], 10) : 0

      return {
        filename,
        part,
        tableNum,
        rows: metadata?.final_rows || 0,
        cols: metadata?.final_cols || 0,
        size: stats.size,
        hasData: (metadata?.final_rows || 0) > 0,
        // Enhanced metadata
        chemicalSystem: metadata?.chemical_system || 'Unknown',
        systemConfidence: metadata?.system_confidence || 'none',
        phasesFound: metadata?.phase_extraction?.phases_found || [],
        columnTypes: metadata?.column_analysis?.summary || null,
      }
    })

    return NextResponse.json({
      success: true,
      count: tables.length,
      tables,
      summary: {
        totalPhaseLabels: summary.total_phase_labels || 0,
        systemsIdentified: summary.systems_identified || 0,
      }
    })

  } catch (error: any) {
    console.error('Error reading enhanced tables:', error)
    return NextResponse.json({
      error: error.message || 'Failed to load enhanced tables',
      tables: []
    }, { status: 500 })
  }
}
