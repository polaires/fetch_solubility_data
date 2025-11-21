"""
Extract all tables from all PDF files (Part2-7)
Shows only summaries to conserve tokens
"""

import tabula
import pandas as pd
from pathlib import Path
import sys

def extract_pdf(pdf_path, output_dir="extracted_data"):
    """Extract all tables from a PDF"""

    if not Path(pdf_path).exists():
        print(f"Error: {pdf_path} not found!")
        return None

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    pdf_name = Path(pdf_path).stem
    print(f"\n{'='*60}")
    print(f"Processing: {pdf_name}")
    print(f"{'='*60}")

    try:
        # Extract ALL tables from ALL pages
        tables = tabula.read_pdf(
            pdf_path,
            pages='all',
            multiple_tables=True,
            pandas_options={'header': None}
        )

        print(f"Found {len(tables)} table(s)")

        # Save each table
        total_rows = 0
        non_empty_tables = 0

        for i, df in enumerate(tables, 1):
            # Skip empty or tiny tables
            if df.empty or len(df) < 2:
                continue

            non_empty_tables += 1
            total_rows += len(df)

            # Save to CSV
            output_file = output_path / f"{pdf_name}_table_{i:03d}.csv"
            df.to_csv(output_file, index=False)

        print(f"✓ Extracted {non_empty_tables} tables, {total_rows} total rows")
        return {"pdf": pdf_name, "tables": non_empty_tables, "rows": total_rows}

    except Exception as e:
        print(f"✗ ERROR: {e}")
        return None

if __name__ == "__main__":
    # Process Part2 through Part7
    parts = [2, 3, 4, 5, 6, 7]

    results = []
    total_tables = 0
    total_rows = 0

    print("Starting extraction of Part2-7...")
    print("This will take several minutes...")

    for part_num in parts:
        pdf_file = f"Data/SDS-31_Part{part_num}.pdf"
        result = extract_pdf(pdf_file)
        if result:
            results.append(result)
            total_tables += result["tables"]
            total_rows += result["rows"]

    print("\n" + "="*60)
    print("EXTRACTION COMPLETE!")
    print("="*60)
    for r in results:
        print(f"{r['pdf']}: {r['tables']} tables, {r['rows']} rows")
    print("="*60)
    print(f"TOTAL: {total_tables} tables, {total_rows} rows")
    print(f"Files saved to: extracted_data/")
