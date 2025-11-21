"""
Step 1: Extract tables from PDF files using tabula-py

This script extracts all tables from PDF files and saves them as CSV files.
"""

import tabula
import pandas as pd
from pathlib import Path
import argparse
import json
from typing import List, Dict
from utils import parse_pdf_filename, ensure_directory


def extract_tables_from_pdf(pdf_path: Path, pages: str = 'all') -> List[pd.DataFrame]:
    """
    Extract all tables from a PDF file

    Args:
        pdf_path: Path to PDF file
        pages: Pages to extract (default: 'all')

    Returns:
        List of DataFrames, one per table
    """
    print(f"Extracting tables from {pdf_path.name}...")

    try:
        tables = tabula.read_pdf(
            str(pdf_path),
            pages=pages,
            multiple_tables=True,
            pandas_options={'header': None}
        )
        return tables

    except Exception as e:
        print(f"  ✗ Error extracting from {pdf_path.name}: {e}")
        return []


def save_tables(tables: List[pd.DataFrame], output_dir: Path, pdf_metadata: Dict) -> List[Dict]:
    """
    Save extracted tables as CSV files

    Args:
        tables: List of DataFrames to save
        output_dir: Directory to save CSV files
        pdf_metadata: Metadata about source PDF

    Returns:
        List of table metadata dicts
    """
    ensure_directory(output_dir)

    table_info_list = []

    for idx, df in enumerate(tables, 1):
        # Generate filename
        table_num = f"{idx:03d}"
        csv_filename = f"{pdf_metadata['stem']}_table_{table_num}.csv"
        csv_path = output_dir / csv_filename

        # Save CSV
        df.to_csv(csv_path, index=False)

        # Collect metadata
        table_info = {
            'file': csv_filename,
            'source_pdf': pdf_metadata['filename'],
            'series': pdf_metadata['series'],
            'part': pdf_metadata['part'],
            'table_num': idx,
            'rows': len(df),
            'cols': len(df.columns),
        }
        table_info_list.append(table_info)

    return table_info_list


def extract_pdf(pdf_path: Path, output_dir: Path, pages: str = 'all') -> Dict:
    """
    Extract all tables from a PDF and save results

    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory for CSV files
        pages: Pages to extract

    Returns:
        Summary dict with extraction results
    """
    # Parse PDF metadata
    pdf_metadata = parse_pdf_filename(pdf_path)

    # Extract tables
    tables = extract_tables_from_pdf(pdf_path, pages)

    if not tables:
        print(f"  ✗ No tables extracted from {pdf_path.name}")
        return {
            'pdf': pdf_path.name,
            'success': False,
            'tables': 0,
            'rows': 0,
        }

    # Save tables
    table_info_list = save_tables(tables, output_dir, pdf_metadata)

    # Calculate summary stats
    total_rows = sum(t['rows'] for t in table_info_list)

    print(f"  ✓ Extracted {len(tables)} tables, {total_rows} rows")

    return {
        'pdf': pdf_path.name,
        'success': True,
        'tables': len(tables),
        'rows': total_rows,
        'metadata': pdf_metadata,
        'table_info': table_info_list,
    }


def extract_all_pdfs(pdf_dir: Path, output_dir: Path) -> Dict:
    """
    Extract tables from all PDFs in a directory

    Args:
        pdf_dir: Directory containing PDF files
        output_dir: Output directory for extracted CSVs

    Returns:
        Summary dict with all extraction results
    """
    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return {'success': False, 'pdfs': 0}

    print("="*80)
    print(f"EXTRACTING TABLES FROM {len(pdf_files)} PDF FILES")
    print("="*80)

    results = []
    total_tables = 0
    total_rows = 0

    for pdf_path in pdf_files:
        result = extract_pdf(pdf_path, output_dir)
        results.append(result)

        if result['success']:
            total_tables += result['tables']
            total_rows += result['rows']

    # Summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"PDFs processed: {len(pdf_files)}")
    print(f"Tables extracted: {total_tables}")
    print(f"Total rows: {total_rows:,}")
    print(f"Output directory: {output_dir}")

    summary = {
        'success': True,
        'pdfs_processed': len(pdf_files),
        'total_tables': total_tables,
        'total_rows': total_rows,
        'results': results,
    }

    # Save extraction manifest
    manifest_path = output_dir / "extraction_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n✓ Extraction manifest saved: {manifest_path}")

    return summary


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Extract tables from PDF files using tabula-py"
    )
    parser.add_argument(
        '--pdf',
        type=Path,
        help='Single PDF file to extract'
    )
    parser.add_argument(
        '--pdf-dir',
        type=Path,
        default=Path('Data'),
        help='Directory containing PDF files (default: Data/)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('output/01_extracted'),
        help='Output directory for extracted CSVs (default: output/01_extracted/)'
    )
    parser.add_argument(
        '--pages',
        default='all',
        help='Pages to extract (default: all)'
    )

    args = parser.parse_args()

    # Single PDF or batch processing
    if args.pdf:
        if not args.pdf.exists():
            print(f"Error: PDF file not found: {args.pdf}")
            return
        result = extract_pdf(args.pdf, args.output, args.pages)
        if result['success']:
            print(f"\n✓ Extraction complete: {result['tables']} tables, {result['rows']} rows")
    else:
        if not args.pdf_dir.exists():
            print(f"Error: PDF directory not found: {args.pdf_dir}")
            return
        summary = extract_all_pdfs(args.pdf_dir, args.output)


if __name__ == "__main__":
    main()
