"""
Extract tables from filtered booklet PDFs.

These are cleaned PDFs containing only data tables.
"""

import tabula
import pandas as pd
from pathlib import Path
import json
from datetime import datetime


def extract_from_filtered_booklets(
    booklet_dir: Path,
    output_dir: Path
) -> dict:
    """
    Extract all tables from filtered booklet PDFs.

    Args:
        booklet_dir: Directory containing filtered PDF files
        output_dir: Where to save extracted CSV tables

    Returns:
        dict with extraction statistics
    """
    booklet_dir = Path(booklet_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        'timestamp': datetime.now().isoformat(),
        'booklets_processed': 0,
        'total_tables': 0,
        'booklets': []
    }

    # Get all filtered PDFs
    pdf_files = sorted(booklet_dir.glob('SDS-*_filtered.pdf'))

    print(f"Found {len(pdf_files)} filtered booklet PDFs")
    print("=" * 70)

    for pdf_file in pdf_files:
        booklet_name = pdf_file.stem  # e.g., "SDS-31_filtered"
        booklet_num = booklet_name.split('-')[1].split('_')[0]  # e.g., "31"

        print(f"\nProcessing {booklet_name}...")

        try:
            # Extract all tables from PDF
            tables = tabula.read_pdf(
                str(pdf_file),
                pages='all',
                multiple_tables=True
            )

            print(f"  Found {len(tables)} tables")

            booklet_results = {
                'booklet': booklet_name,
                'pdf_file': pdf_file.name,
                'tables_extracted': len(tables),
                'tables': []
            }

            # Save each table
            for idx, df in enumerate(tables, 1):
                if df.empty:
                    print(f"    Table {idx}: Empty - skipped")
                    continue

                # Generate filename
                table_filename = f"SDS-{booklet_num}_table_{idx:03d}.csv"
                output_path = output_dir / table_filename

                # Save raw extracted table
                df.to_csv(output_path, index=False)

                print(f"    Table {idx}: {df.shape[0]} rows × {df.shape[1]} cols → {table_filename}")

                booklet_results['tables'].append({
                    'filename': table_filename,
                    'table_number': idx,
                    'rows': int(df.shape[0]),
                    'cols': int(df.shape[1])
                })

                results['total_tables'] += 1

            results['booklets_processed'] += 1
            results['booklets'].append(booklet_results)

        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue

    # Save extraction report
    report_file = output_dir / '_extraction_report.json'
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)

    return results


def main():
    """Extract tables from all filtered booklets."""
    print("=" * 70)
    print("FILTERED BOOKLET TABLE EXTRACTION")
    print("=" * 70)

    booklet_dir = Path('filtered_booklet')
    output_dir = Path('output/filtered_extracted')

    if not booklet_dir.exists():
        print(f"Error: Booklet directory not found: {booklet_dir}")
        return

    # Extract tables
    results = extract_from_filtered_booklets(booklet_dir, output_dir)

    # Print summary
    print(f"\n{'=' * 70}")
    print("EXTRACTION COMPLETE")
    print(f"{'=' * 70}")
    print(f"Booklets processed: {results['booklets_processed']}")
    print(f"Total tables extracted: {results['total_tables']}")
    print(f"\nTables saved to: {output_dir}")
    print(f"Report saved to: {output_dir}/_extraction_report.json")

    # Show breakdown by booklet
    print(f"\nBreakdown by booklet:")
    for booklet in results['booklets']:
        print(f"  {booklet['booklet']}: {booklet['tables_extracted']} tables")


if __name__ == '__main__':
    main()
