# Filtered Booklet Data - Searchable Database

This directory contains processed and searchable solubility data extracted from 12 filtered PDF booklets.

## Overview

- **Source**: 12 PDF files in `filtered_booklet/` directory
- **Tables Extracted**: 307 tables
- **Total Data Rows**: 3,803 rows
- **Processing Date**: 2025-11-22

## Directory Structure

```
filtered_booklet/                    # Original PDF files (12 PDFs)
output/filtered_booklet/
  ├── 01_extracted/                  # Raw extracted tables (307 CSV files)
  ├── 02_cleaned/                    # Cleaned tables with OCR fixes (307 CSV files)
  └── database/                      # Searchable database
      ├── master_index.json          # Complete index of all tables
      ├── consolidated_data.csv      # All data in one CSV file
      ├── solubility_data.db         # SQLite database
      └── search_data.py             # Search interface script
```

## PDF Sources

| PDF File | Tables | Description |
|----------|--------|-------------|
| SDS-13_filtered | 21 | Solubility Data Series Volume 13 |
| SDS-14_filtered | 14 | Solubility Data Series Volume 14 |
| SDS-23_filtered | 18 | Solubility Data Series Volume 23 |
| SDS-30_filtered | 33 | Solubility Data Series Volume 30 |
| SDS-31_filtered | 16 | Solubility Data Series Volume 31 |
| SDS-41_filtered | 2  | Solubility Data Series Volume 41 |
| SDS-44_filtered | 11 | Solubility Data Series Volume 44 |
| SDS-47_filtered | 147| Solubility Data Series Volume 47 |
| SDS-52_filtered | 21 | Solubility Data Series Volume 52 |
| SDS-55_filtered | 13 | Solubility Data Series Volume 55 |
| SDS-61_filtered | 9  | Solubility Data Series Volume 61 |
| SDS-65_filtered | 2  | Solubility Data Series Volume 65 |

## Quick Start

### 1. View the Index

```bash
python output/filtered_booklet/database/search_data.py --index
```

### 2. Search by Text

Search for any text (chemical name, formula, etc.):

```bash
python output/filtered_booklet/database/search_data.py --query "Na2SO4"
python output/filtered_booklet/database/search_data.py --query "molality"
```

### 3. Search by PDF Source

Get all data from a specific PDF:

```bash
python output/filtered_booklet/database/search_data.py --pdf SDS-13
python output/filtered_booklet/database/search_data.py --pdf SDS-47
```

### 4. Search by Data Type

Find tables containing specific data types:

```bash
python output/filtered_booklet/database/search_data.py --type molality
python output/filtered_booklet/database/search_data.py --type mass_percent
python output/filtered_booklet/database/search_data.py --type temperature
```

### 5. Custom SQL Queries

Use the SQLite database for advanced queries:

```bash
python output/filtered_booklet/database/search_data.py --sql "SELECT * FROM solubility_data WHERE pdf_source = 'SDS-31_filtered' LIMIT 10"
```

### 6. Export Results

Save search results to a CSV file:

```bash
python output/filtered_booklet/database/search_data.py --query "sulfate" --output results.csv
```

## Database Schema

### SQLite Tables

#### `solubility_data`
- Main table containing all extracted data
- Columns vary by source table (20 columns total after consolidation)
- Includes metadata: `source_file`, `pdf_source`, `table_types`

#### `pdf_sources`
- Summary of PDF sources
- Columns: `pdf_source`, `table_count`

#### `table_metadata`
- Detailed metadata for each table
- Columns: `filename`, `rows`, `cols`, `has_numeric_data`, `data_types`, `chemicals`

## Files Generated

### 1. Master Index (`master_index.json`)
Complete index with metadata for all 307 tables:
- Table counts by PDF source
- Data types identified in each table
- Row and column counts
- Chemical compounds detected

### 2. Consolidated CSV (`consolidated_data.csv`)
All 3,803 rows combined into a single CSV file with source tracking.

### 3. SQLite Database (`solubility_data.db`)
Queryable database with three tables for efficient searching.

## Data Types Detected

The extraction pipeline identifies these data types:
- `mass_percent` - Mass percentage data
- `mol_percent` - Molar percentage data
- `molality` - Molality (mol/kg) data
- `temperature` - Temperature data
- `phase` - Phase information
- `solubility` - Solubility measurements

## Processing Pipeline

To reprocess the data:

```bash
# Extract and clean all PDFs
python pipeline.py --all --config config_filtered_booklet.yaml

# Create searchable database
python create_searchable_database.py
```

## Configuration

The processing uses `config_filtered_booklet.yaml` with:
- OCR artifact correction
- Decimal separator fixes
- Number formatting cleanup
- Phase marker extraction

## Notes

- Some tables contain OCR artifacts that have been automatically corrected
- Empty or malformed tables are included but may need manual review
- The largest source is SDS-47_filtered with 147 tables
- Data types are automatically detected but may need verification

## Examples

### Find all temperature data
```bash
python output/filtered_booklet/database/search_data.py --type temperature --limit 20
```

### Search for a specific compound
```bash
python output/filtered_booklet/database/search_data.py --query "NaCl" --output nacl_data.csv
```

### Get statistics by PDF
```sql
SELECT pdf_source, COUNT(*) as row_count
FROM solubility_data
GROUP BY pdf_source
ORDER BY row_count DESC;
```

Run with:
```bash
python output/filtered_booklet/database/search_data.py --sql "SELECT pdf_source, COUNT(*) as row_count FROM solubility_data GROUP BY pdf_source ORDER BY row_count DESC"
```

## Contact

For issues or questions about the data extraction, refer to the main project README.
