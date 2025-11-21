/**
 * Database configuration for future Postgres integration
 *
 * This file is prepared for when you want to migrate from CSV files
 * to a Postgres database for better performance and querying.
 */

import { Pool } from 'pg'

// Singleton pattern for database connection
let pool: Pool | null = null

export function getPool(): Pool {
  if (!pool) {
    pool = new Pool({
      connectionString: process.env.DATABASE_URL,
      // For Vercel Postgres, use these settings:
      ssl: process.env.NODE_ENV === 'production' ? {
        rejectUnauthorized: false
      } : undefined,
      // Connection pool settings
      max: 20, // Maximum number of clients
      idleTimeoutMillis: 30000,
      connectionTimeoutMillis: 2000,
    })

    // Handle pool errors
    pool.on('error', (err) => {
      console.error('Unexpected database pool error:', err)
    })
  }

  return pool
}

/**
 * Execute a query with parameters
 */
export async function query(text: string, params?: any[]) {
  const pool = getPool()
  const start = Date.now()
  const result = await pool.query(text, params)
  const duration = Date.now() - start
  console.log('Executed query', { text, duration, rows: result.rowCount })
  return result
}

/**
 * Get a client from the pool for transactions
 */
export async function getClient() {
  const pool = getPool()
  return await pool.connect()
}

/**
 * Close the database pool
 */
export async function closePool() {
  if (pool) {
    await pool.end()
    pool = null
  }
}

/**
 * Schema for solubility data table (for future use)
 *
 * To migrate CSV data to Postgres:
 * 1. Set up Vercel Postgres
 * 2. Run the migration SQL below
 * 3. Import CSV data using scripts/migrate_to_postgres.ts
 */
export const SCHEMA_SQL = `
-- Main solubility data table
CREATE TABLE IF NOT EXISTS solubility_data (
  id SERIAL PRIMARY KEY,
  source_file VARCHAR(255) NOT NULL,
  pdf_part VARCHAR(50) NOT NULL,
  table_number INTEGER NOT NULL,
  row_number INTEGER NOT NULL,

  -- Data columns (will vary by table)
  -- These are examples based on common columns
  component_1_mass_percent DECIMAL(10, 6),
  component_1_molality DECIMAL(10, 6),
  component_1_mol_percent DECIMAL(10, 6),
  component_2_mass_percent DECIMAL(10, 6),
  component_2_molality DECIMAL(10, 6),
  phase VARCHAR(20),
  temperature_c DECIMAL(10, 2),
  temperature_k DECIMAL(10, 2),

  -- Metadata
  raw_data JSONB, -- Store full row as JSON
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  -- Indexes
  INDEX idx_pdf_part (pdf_part),
  INDEX idx_table_number (table_number),
  INDEX idx_phase (phase),
  INDEX idx_source_file (source_file)
);

-- Table metadata
CREATE TABLE IF NOT EXISTS table_metadata (
  id SERIAL PRIMARY KEY,
  filename VARCHAR(255) UNIQUE NOT NULL,
  pdf_part VARCHAR(50) NOT NULL,
  table_number INTEGER NOT NULL,
  rows_count INTEGER,
  cols_count INTEGER,
  has_phase_data BOOLEAN DEFAULT FALSE,
  has_temperature BOOLEAN DEFAULT FALSE,
  has_mass_percent BOOLEAN DEFAULT FALSE,
  has_molality BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Full-text search support
CREATE INDEX IF NOT EXISTS idx_solubility_data_search
  ON solubility_data USING GIN(raw_data);
`

/**
 * Example query functions (for future use with Postgres)
 */

export interface SolubilityQuery {
  part?: string
  tableNumber?: number
  phase?: string
  minTemp?: number
  maxTemp?: number
  limit?: number
  offset?: number
}

export async function searchSolubilityData(params: SolubilityQuery) {
  const conditions: string[] = []
  const values: any[] = []
  let paramCounter = 1

  if (params.part) {
    conditions.push(`pdf_part = $${paramCounter}`)
    values.push(params.part)
    paramCounter++
  }

  if (params.tableNumber !== undefined) {
    conditions.push(`table_number = $${paramCounter}`)
    values.push(params.tableNumber)
    paramCounter++
  }

  if (params.phase) {
    conditions.push(`phase = $${paramCounter}`)
    values.push(params.phase)
    paramCounter++
  }

  if (params.minTemp !== undefined) {
    conditions.push(`temperature_c >= $${paramCounter}`)
    values.push(params.minTemp)
    paramCounter++
  }

  if (params.maxTemp !== undefined) {
    conditions.push(`temperature_c <= $${paramCounter}`)
    values.push(params.maxTemp)
    paramCounter++
  }

  const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : ''
  const limit = params.limit || 100
  const offset = params.offset || 0

  const sql = `
    SELECT * FROM solubility_data
    ${whereClause}
    ORDER BY pdf_part, table_number, row_number
    LIMIT $${paramCounter} OFFSET $${paramCounter + 1}
  `

  values.push(limit, offset)

  return await query(sql, values)
}
