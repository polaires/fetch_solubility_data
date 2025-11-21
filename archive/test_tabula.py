"""
Simple test script for tabula-py
Tests extraction on just a few pages to verify it works
"""

import tabula
import pandas as pd
from pathlib import Path

def test_tabula_extraction():
    """Test tabula on a small portion of one PDF"""

    # Use Part 1 (larger PDF with more pages)
    pdf_path = "Data/SDS-31_Part1.pdf"

    if not Path(pdf_path).exists():
        print(f"Error: {pdf_path} not found!")
        return

    print(f"Testing tabula-py on: {pdf_path}")
    print(f"Extracting pages 20-30 (looking for binary aqueous data)")
    print("="*60)

    try:
        # Extract tables from pages 20-30
        tables = tabula.read_pdf(
            pdf_path,
            pages='20-30',
            multiple_tables=True,
            pandas_options={'header': None}
        )

        print(f"\n✓ SUCCESS: Found {len(tables)} table(s)")

        # Display info about each table
        for i, df in enumerate(tables, 1):
            print(f"\nTable {i}:")
            print(f"  Shape: {df.shape[0]} rows x {df.shape[1]} columns")
            print(f"  Preview (first 5 rows):")
            print(df.head())

            # Save to CSV for inspection
            output_dir = Path("test_output")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"test_table_{i}.csv"
            df.to_csv(output_file, index=False)
            print(f"  Saved to: {output_file}")

        print("\n" + "="*60)
        print("✓ Tabula test PASSED - extraction working!")
        print("="*60)

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print(f"Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tabula_extraction()
