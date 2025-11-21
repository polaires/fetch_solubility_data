"""
Quick Extraction Script
========================
Simple script to quickly extract tables from SDS-31 PDFs
without needing all dependencies installed.

This script will work with whatever PDF libraries you have available.
"""

import os
from pathlib import Path

def extract_with_available_tools():
    """Extract using whatever tools are available"""

    print("Checking available PDF extraction tools...")
    print("=" * 60)

    # Check pdfplumber (easiest to install, no system dependencies)
    try:
        import pdfplumber
        print("✓ pdfplumber is available")
        has_pdfplumber = True
    except ImportError:
        print("✗ pdfplumber not installed")
        print("  Install with: pip install pdfplumber")
        has_pdfplumber = False

    # Check tabula
    try:
        import tabula
        print("✓ tabula-py is available")
        has_tabula = True
    except ImportError:
        print("✗ tabula-py not installed")
        print("  Install with: pip install tabula-py")
        print("  (Also requires Java)")
        has_tabula = False

    # Check camelot
    try:
        import camelot
        print("✓ camelot-py is available")
        has_camelot = True
    except ImportError:
        print("✗ camelot-py not installed")
        print("  Install with: pip install 'camelot-py[base]'")
        print("  (Also requires Ghostscript)")
        has_camelot = False

    print("=" * 60)

    if not any([has_pdfplumber, has_tabula, has_camelot]):
        print("\n❌ No PDF extraction tools available!")
        print("\nQuickest option: pip install pdfplumber")
        return False

    print("\n📂 Looking for PDF files...")
    data_dir = Path("Data")

    if not data_dir.exists():
        print(f"❌ {data_dir} directory not found!")
        return False

    pdf_files = sorted(data_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in {data_dir}")
        return False

    print(f"✓ Found {len(pdf_files)} PDF files")

    # Use the smallest PDF for testing
    target_pdf = data_dir / "SDS-31_Part7.pdf"

    if not target_pdf.exists():
        print(f"❌ {target_pdf} not found!")
        return False

    print(f"\n📄 Testing extraction on: {target_pdf.name}")
    print(f"   File size: {target_pdf.stat().st_size / 1024 / 1024:.1f} MB")

    output_dir = Path("extracted_data")
    output_dir.mkdir(exist_ok=True)

    # Try pdfplumber first (most reliable, no system dependencies)
    if has_pdfplumber:
        print("\n" + "=" * 60)
        print("Extracting with pdfplumber (recommended)...")
        print("=" * 60)

        import pdfplumber
        import pandas as pd

        try:
            table_count = 0
            with pdfplumber.open(str(target_pdf)) as pdf:
                # Test on pages 10-20 only
                for page_num in range(9, min(20, len(pdf.pages))):
                    page = pdf.pages[page_num]
                    tables = page.extract_tables()

                    for table in tables:
                        if not table or len(table) < 2:
                            continue

                        # Convert to DataFrame
                        df = pd.DataFrame(table[1:], columns=table[0])

                        if df.empty:
                            continue

                        table_count += 1
                        output_file = output_dir / f"table_page{page_num+1}_{table_count}.csv"
                        df.to_csv(output_file, index=False)
                        print(f"  ✓ Page {page_num+1}: {df.shape[0]}x{df.shape[1]} -> {output_file.name}")

            if table_count > 0:
                print(f"\n✅ Successfully extracted {table_count} tables!")
                print(f"📁 Saved to: {output_dir}/")
                return True
            else:
                print("\n⚠️  No tables found on pages 10-20")

        except Exception as e:
            print(f"❌ Error: {e}")

    # Try tabula
    if has_tabula and not has_pdfplumber:
        print("\n" + "=" * 60)
        print("Extracting with tabula-py...")
        print("=" * 60)

        import tabula

        try:
            tables = tabula.read_pdf(
                str(target_pdf),
                pages='10-20',
                multiple_tables=True
            )

            for i, df in enumerate(tables):
                if df.empty:
                    continue

                output_file = output_dir / f"tabula_table_{i+1}.csv"
                df.to_csv(output_file, index=False)
                print(f"  ✓ Table {i+1}: {df.shape[0]}x{df.shape[1]} -> {output_file.name}")

            if len(tables) > 0:
                print(f"\n✅ Successfully extracted {len(tables)} tables!")
                print(f"📁 Saved to: {output_dir}/")
                return True

        except Exception as e:
            print(f"❌ Error: {e}")

    return False


if __name__ == "__main__":
    print("\n" + "🔬" * 30)
    print("  Solubility Data Quick Extraction Tool")
    print("🔬" * 30 + "\n")

    success = extract_with_available_tools()

    if success:
        print("\n" + "=" * 60)
        print("Next steps:")
        print("=" * 60)
        print("1. Review the extracted CSV files in extracted_data/")
        print("2. Check if the data quality is good")
        print("3. Run extract_solubility_data.py for full extraction")
        print("4. Adjust page ranges or methods as needed")
    else:
        print("\n" + "=" * 60)
        print("Troubleshooting:")
        print("=" * 60)
        print("1. Install pdfplumber: pip install pdfplumber")
        print("2. Or install all tools: pip install -r requirements.txt")
        print("3. Check that PDF files are in the Data/ directory")
