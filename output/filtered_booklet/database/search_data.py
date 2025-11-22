#!/usr/bin/env python3
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

    print("\n=== MASTER INDEX ===")
    print(f"Total tables: {index['total_files']}")
    print(f"Total rows: {index['total_rows']:,}")
    print(f"\nPDF Sources:")
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
        print(f"\n=== SEARCH RESULTS ===")
        print(f"Found {len(df)} rows")

        if len(df) > args.limit:
            print(f"Showing first {args.limit} results (use --limit to change)")
            df = df.head(args.limit)

        print("\n" + df.to_string())

        if args.output:
            df.to_csv(args.output, index=False)
            print(f"\n✓ Results saved to: {args.output}")


if __name__ == "__main__":
    main()
