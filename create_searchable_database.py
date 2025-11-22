#!/usr/bin/env python3
"""
Create a searchable database from filtered booklet data

This script consolidates all extracted and cleaned tables into:
1. A master index (JSON)
2. A consolidated CSV database
3. A SQLite database for queries
4. A search index for fast lookups
"""

import pandas as pd
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import re
from typing import List, Dict, Any


def load_manifest(manifest_path: Path) -> Dict:
    """Load the extraction/cleaning manifest"""
    if manifest_path.exists():
        with open(manifest_path) as f:
            return json.load(f)
    return {}


def identify_table_type(df: pd.DataFrame, filename: str) -> Dict[str, Any]:
    """
    Identify what type of data this table contains

    Returns metadata about the table
    """
    metadata = {
        'filename': filename,
        'rows': len(df),
        'cols': len(df.columns),
        'has_numeric_data': False,
        'data_types': [],
        'chemicals': []
    }

    # Check first few rows for headers/content
    header_text = ' '.join([str(val) for val in df.iloc[:3].values.flatten() if pd.notna(val)]).lower()

    # Identify data types
    if 'mass%' in header_text or 'mass  %' in header_text:
        metadata['data_types'].append('mass_percent')
    if 'mol%' in header_text or 'mol  %' in header_text:
        metadata['data_types'].append('mol_percent')
    if 'mol/kg' in header_text or 'molkg' in header_text or 'molality' in header_text:
        metadata['data_types'].append('molality')
    if 'temp' in header_text or '°c' in header_text:
        metadata['data_types'].append('temperature')
    if 'phase' in header_text:
        metadata['data_types'].append('phase')
    if 'solubility' in header_text:
        metadata['data_types'].append('solubility')

    # Check for numeric data
    for val in df.values.flatten():
        if pd.notna(val) and re.search(r'\d+\.?\d*', str(val)):
            metadata['has_numeric_data'] = True
            break

    # Try to identify chemical compounds
    all_text = ' '.join([str(val) for val in df.values.flatten() if pd.notna(val)])

    # Common chemical patterns
    chemical_patterns = [
        r'\b[A-Z][a-z]?(?:[A-Z][a-z]?)*\d*\b',  # Chemical formulas
        r'\b(?:Na|K|Ca|Mg|Li|NH4)\d*[A-Z][a-z]*\d*\b',  # Salts
        r'\b\w+(?:ate|ide|ite)\b',  # Chemical names ending in -ate, -ide, -ite
    ]

    for pattern in chemical_patterns:
        matches = re.findall(pattern, all_text)
        if matches:
            metadata['chemicals'].extend(matches[:5])  # Limit to first 5

    metadata['chemicals'] = list(set(metadata['chemicals']))[:10]  # Deduplicate and limit

    return metadata


def create_master_index(cleaned_dir: Path, output_dir: Path):
    """Create a master index of all tables"""
    print("Creating master index...")

    index = {
        'created': datetime.now().isoformat(),
        'source_directory': str(cleaned_dir),
        'total_files': 0,
        'total_rows': 0,
        'pdf_sources': {},
        'tables': []
    }

    pdf_counts = {}

    # Process all CSV files
    for csv_file in sorted(cleaned_dir.glob("*.csv")):
        # Extract PDF source from filename (e.g., SDS-13_filtered)
        match = re.match(r'(SDS-\d+_filtered)', csv_file.stem)
        pdf_source = match.group(1) if match else 'unknown'

        if pdf_source not in pdf_counts:
            pdf_counts[pdf_source] = 0
        pdf_counts[pdf_source] += 1

        try:
            df = pd.read_csv(csv_file)
            metadata = identify_table_type(df, csv_file.name)

            # Add to index
            table_entry = {
                'file': csv_file.name,
                'pdf_source': pdf_source,
                'path': str(csv_file.relative_to(cleaned_dir.parent)),
                **metadata
            }

            index['tables'].append(table_entry)
            index['total_files'] += 1
            index['total_rows'] += len(df)

        except Exception as e:
            print(f"  Warning: Could not process {csv_file.name}: {e}")

    # Update PDF sources summary
    index['pdf_sources'] = {
        pdf: {'table_count': count}
        for pdf, count in sorted(pdf_counts.items())
    }

    # Save index
    index_path = output_dir / 'master_index.json'
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)

    print(f"  ✓ Master index created: {index_path}")
    print(f"  - {index['total_files']} tables indexed")
    print(f"  - {index['total_rows']:,} total rows")
    print(f"  - {len(index['pdf_sources'])} PDF sources")

    return index


def create_consolidated_database(cleaned_dir: Path, output_dir: Path, index: Dict):
    """Create consolidated CSV and SQLite databases"""
    print("\nCreating consolidated databases...")

    # Prepare consolidated data
    all_data = []

    for table_info in index['tables']:
        csv_path = cleaned_dir / table_info['file']

        try:
            df = pd.read_csv(csv_path)

            # Add metadata columns
            df['source_file'] = table_info['file']
            df['pdf_source'] = table_info['pdf_source']
            df['table_types'] = ', '.join(table_info['data_types'])

            all_data.append(df)

        except Exception as e:
            print(f"  Warning: Could not load {csv_path.name}: {e}")

    # Combine all data
    if all_data:
        consolidated_df = pd.concat(all_data, ignore_index=True, sort=False)

        # Save as CSV
        csv_path = output_dir / 'consolidated_data.csv'
        consolidated_df.to_csv(csv_path, index=False)
        print(f"  ✓ Consolidated CSV: {csv_path}")
        print(f"    - {len(consolidated_df):,} rows")
        print(f"    - {len(consolidated_df.columns)} columns")

        # Create SQLite database
        db_path = output_dir / 'solubility_data.db'
        conn = sqlite3.connect(db_path)

        # Store main data
        consolidated_df.to_sql('solubility_data', conn, if_exists='replace', index=False)

        # Create index tables for fast lookup
        pdf_sources = pd.DataFrame([
            {'pdf_source': pdf, 'table_count': info['table_count']}
            for pdf, info in index['pdf_sources'].items()
        ])
        pdf_sources.to_sql('pdf_sources', conn, if_exists='replace', index=False)

        # Create metadata table (convert lists to JSON strings for SQLite)
        metadata_df = pd.DataFrame(index['tables'])
        for col in metadata_df.columns:
            if metadata_df[col].apply(lambda x: isinstance(x, list)).any():
                metadata_df[col] = metadata_df[col].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)
        metadata_df.to_sql('table_metadata', conn, if_exists='replace', index=False)

        conn.close()
        print(f"  ✓ SQLite database: {db_path}")
        print(f"    - Tables: solubility_data, pdf_sources, table_metadata")

        return consolidated_df

    return None


def create_search_interface(output_dir: Path):
    """Create a simple search script"""
    print("\nCreating search interface...")

    search_script = '''#!/usr/bin/env python3
"""
Simple search interface for filtered booklet data

Usage:
    python search_data.py --query "Na2SO4"
    python search_data.py --pdf SDS-13
    python search_data.py --type molality
    python search_data.py --sql "SELECT * FROM solubility_data WHERE pdf_source = 'SDS-13_filtered' LIMIT 10"
"""

import argparse
import sqlite3
import pandas as pd
import json
from pathlib import Path


def search_by_text(db_path, query):
    """Search for text in any column"""
    conn = sqlite3.connect(db_path)

    # Get all column names
    cursor = conn.execute("SELECT * FROM solubility_data LIMIT 1")
    columns = [desc[0] for desc in cursor.description]

    # Build OR query for all columns
    where_clauses = [f"{col} LIKE ?" for col in columns]
    query_sql = f"SELECT * FROM solubility_data WHERE {' OR '.join(where_clauses)}"

    params = [f'%{query}%'] * len(columns)

    df = pd.read_sql_query(query_sql, conn, params=params)
    conn.close()

    return df


def search_by_pdf(db_path, pdf_source):
    """Search by PDF source"""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        "SELECT * FROM solubility_data WHERE pdf_source LIKE ?",
        conn,
        params=[f'%{pdf_source}%']
    )
    conn.close()
    return df


def search_by_type(db_path, data_type):
    """Search by data type"""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(
        "SELECT * FROM solubility_data WHERE table_types LIKE ?",
        conn,
        params=[f'%{data_type}%']
    )
    conn.close()
    return df


def execute_sql(db_path, sql):
    """Execute custom SQL query"""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


def show_index(index_path):
    """Show the master index"""
    with open(index_path) as f:
        index = json.load(f)

    print("\\n=== MASTER INDEX ===")
    print(f"Total tables: {index['total_files']}")
    print(f"Total rows: {index['total_rows']:,}")
    print(f"\\nPDF Sources:")
    for pdf, info in index['pdf_sources'].items():
        print(f"  {pdf}: {info['table_count']} tables")


def main():
    parser = argparse.ArgumentParser(description="Search filtered booklet data")
    parser.add_argument('--query', help='Text search query')
    parser.add_argument('--pdf', help='Search by PDF source (e.g., SDS-13)')
    parser.add_argument('--type', help='Search by data type (e.g., molality, mass_percent)')
    parser.add_argument('--sql', help='Execute custom SQL query')
    parser.add_argument('--index', action='store_true', help='Show master index')
    parser.add_argument('--limit', type=int, default=50, help='Limit results (default: 50)')
    parser.add_argument('--output', help='Save results to CSV file')

    args = parser.parse_args()

    # Paths (script is in the database directory)
    output_dir = Path(__file__).parent
    db_path = output_dir / 'solubility_data.db'
    index_path = output_dir / 'master_index.json'

    if args.index:
        show_index(index_path)
        return

    # Execute search
    df = None

    if args.sql:
        df = execute_sql(db_path, args.sql)
    elif args.query:
        df = search_by_text(db_path, args.query)
    elif args.pdf:
        df = search_by_pdf(db_path, args.pdf)
    elif args.type:
        df = search_by_type(db_path, args.type)
    else:
        parser.print_help()
        return

    # Display results
    if df is not None:
        print(f"\\n=== SEARCH RESULTS ===")
        print(f"Found {len(df)} rows")

        if len(df) > args.limit:
            print(f"Showing first {args.limit} results (use --limit to change)")
            df = df.head(args.limit)

        print("\\n" + df.to_string())

        if args.output:
            df.to_csv(args.output, index=False)
            print(f"\\n✓ Results saved to: {args.output}")


if __name__ == "__main__":
    main()
'''

    search_path = output_dir / 'search_data.py'
    with open(search_path, 'w') as f:
        f.write(search_script)

    search_path.chmod(0o755)
    print(f"  ✓ Search script created: {search_path}")
    print(f"\n  Usage examples:")
    print(f"    python {search_path} --index")
    print(f"    python {search_path} --query 'Na2SO4'")
    print(f"    python {search_path} --pdf SDS-13")
    print(f"    python {search_path} --type molality")


def main():
    print("="*80)
    print("CREATING SEARCHABLE DATABASE FROM FILTERED BOOKLET DATA")
    print("="*80)

    # Paths
    cleaned_dir = Path('output/filtered_booklet/02_cleaned')
    output_dir = Path('output/filtered_booklet/database')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create master index
    index = create_master_index(cleaned_dir, output_dir)

    # Create consolidated databases
    create_consolidated_database(cleaned_dir, output_dir, index)

    # Create search interface
    create_search_interface(output_dir)

    print("\n" + "="*80)
    print("✓ SEARCHABLE DATABASE CREATED SUCCESSFULLY")
    print("="*80)
    print(f"\nDatabase location: {output_dir}")
    print(f"\nFiles created:")
    print(f"  1. master_index.json - Complete index of all tables")
    print(f"  2. consolidated_data.csv - All data in one CSV")
    print(f"  3. solubility_data.db - SQLite database")
    print(f"  4. search_data.py - Search interface script")


if __name__ == "__main__":
    main()
