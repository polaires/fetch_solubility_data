"""
Simple PDF Table Extraction Script
===================================
Minimal script to extract tables from SDS-31 PDFs using only pdfplumber.

Install with: pip install pdfplumber pandas

Usage: python simple_extract.py
"""

import pdfplumber
import pandas as pd
from pathlib import Path

def main():
    # Configuration
    pdf_path = "Data/SDS-31_Part7.pdf"  # Change this to process different files
    start_page = 10  # Start from page 10 (1-indexed)
    end_page = 30    # End at page 30 (1-indexed)
    output_dir = Path("extracted_data")

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Simple Solubility Data Extraction")
    print("=" * 60)
    print(f"PDF: {pdf_path}")
    print(f"Pages: {start_page}-{end_page}")
    print(f"Output: {output_dir}/")
    print("=" * 60)

    # Check if PDF exists
    if not Path(pdf_path).exists():
        print(f"\nError: {pdf_path} not found!")
        print("Please make sure the PDF is in the Data/ directory.")
        return

    # Open and process PDF
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"\nPDF has {total_pages} pages total\n")

            table_count = 0

            # Process each page
            for page_num in range(start_page - 1, min(end_page, total_pages)):
                page = pdf.pages[page_num]
                actual_page = page_num + 1

                # Extract tables from this page
                tables = page.extract_tables()

                if not tables:
                    print(f"Page {actual_page}: No tables found")
                    continue

                # Process each table on the page
                for table_idx, table in enumerate(tables):
                    # Skip empty tables
                    if not table or len(table) < 2:
                        continue

                    # Convert to DataFrame
                    # Assume first row is header
                    try:
                        df = pd.DataFrame(table[1:], columns=table[0])

                        # Skip if no data
                        if df.empty:
                            continue

                        # Generate filename
                        table_count += 1
                        filename = f"table_page{actual_page}_{table_idx + 1}.csv"
                        filepath = output_dir / filename

                        # Save to CSV
                        df.to_csv(filepath, index=False)

                        print(f"✓ Page {actual_page}, Table {table_idx + 1}: "
                              f"{df.shape[0]} rows × {df.shape[1]} cols → {filename}")

                    except Exception as e:
                        print(f"✗ Page {actual_page}, Table {table_idx + 1}: Error - {e}")

            # Summary
            print("\n" + "=" * 60)
            if table_count > 0:
                print(f"✅ Success! Extracted {table_count} tables")
                print(f"📁 Files saved to: {output_dir}/")
                print("\nNext steps:")
                print("1. Open the CSV files to review the extracted data")
                print("2. Check if the table structure looks correct")
                print("3. Adjust start_page/end_page if needed")
                print("4. Process other PDF parts if satisfied with results")
            else:
                print("⚠️  No tables were extracted")
                print("\nTroubleshooting:")
                print("1. Check if the page range contains actual data tables")
                print("2. Index pages (1-9) usually don't have data tables")
                print("3. Try different page ranges, e.g., pages 20-40")
            print("=" * 60)

    except FileNotFoundError:
        print(f"\n❌ Error: Could not find {pdf_path}")
        print("Make sure the PDF file exists in the Data/ directory")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nIf you see import errors, install dependencies:")
        print("  pip install pdfplumber pandas")


if __name__ == "__main__":
    # Check dependencies
    try:
        import pdfplumber
        import pandas as pd
        main()
    except ImportError as e:
        print("=" * 60)
        print("Missing Dependencies")
        print("=" * 60)
        print(f"\nError: {e}")
        print("\nPlease install required packages:")
        print("  pip install pdfplumber pandas")
        print("\nOr install all dependencies:")
        print("  pip install -r requirements.txt")
        print("=" * 60)
