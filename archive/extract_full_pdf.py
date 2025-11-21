"""
Extract all tables from a full PDF using tabula-py
Shows only summaries to conserve tokens
"""

import tabula
import pandas as pd
from pathlib import Path
import sys

def extract_full_pdf(pdf_path, output_dir="extracted_data"):
    """Extract all tables from entire PDF"""

    if not Path(pdf_path).exists():
        print(f"Error: {pdf_path} not found!")
        return

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    pdf_name = Path(pdf_path).stem
    print(f"Extracting ALL tables from: {pdf_path}")
    print(f"Output directory: {output_dir}/")
    print("="*60)

    try:
        # Extract ALL tables from ALL pages
        print("\nExtracting tables... (this may take a minute)")
        tables = tabula.read_pdf(
            pdf_path,
            pages='all',
            multiple_tables=True,
            pandas_options={'header': None}
        )

        print(f"\n✓ SUCCESS: Found {len(tables)} table(s) in entire PDF")
        print("="*60)

        # Save each table and show summary only
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

            # Show brief summary (not full data to save tokens)
            print(f"Table {i:3d}: {df.shape[0]:4d} rows × {df.shape[1]:2d} cols → {output_file.name}")

        print("="*60)
        print(f"\n✓ Extraction Complete!")
        print(f"  Total tables extracted: {non_empty_tables}")
        print(f"  Total rows: {total_rows}")
        print(f"  Files saved to: {output_path}/")
        print("\nTo examine data, open the CSV files in the extracted_data/ directory")

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print(f"Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Default to Part1, but allow command line argument
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    else:
        pdf_file = "Data/SDS-31_Part1.pdf"

    extract_full_pdf(pdf_file)
