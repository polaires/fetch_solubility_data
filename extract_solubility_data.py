"""
Solubility Data Extraction Tool
================================
Extract solubility data tables from SDS-31 (Alkali Metal Orthophosphates) PDFs

This script uses multiple PDF extraction libraries to accurately extract
binary aqueous system solubility data from scientific PDFs.

Tools used:
- Camelot: Best for tables with clear borders (Lattice mode)
- Tabula: Good for scientific document tables
- pdfplumber: Fine control for complex tables
"""

import os
import sys
from pathlib import Path
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False
    print("Warning: Camelot not installed. Install with: pip install 'camelot-py[base]'")

try:
    import tabula
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False
    print("Warning: Tabula not installed. Install with: pip install tabula-py")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("Warning: pdfplumber not installed. Install with: pip install pdfplumber")


class SolubilityDataExtractor:
    """Extract solubility data from PDF files using multiple methods"""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.filename = Path(pdf_path).stem
        self.output_dir = Path("extracted_data")
        self.output_dir.mkdir(exist_ok=True)

    def extract_with_camelot(self, pages='all', flavor='lattice'):
        """
        Extract tables using Camelot

        Args:
            pages: Page numbers to extract (default: 'all')
            flavor: 'lattice' for bordered tables, 'stream' for borderless
        """
        if not CAMELOT_AVAILABLE:
            print("Camelot not available. Skipping.")
            return None

        print(f"\n{'='*60}")
        print(f"Extracting with Camelot ({flavor} mode)...")
        print(f"{'='*60}")

        try:
            tables = camelot.read_pdf(
                self.pdf_path,
                pages=pages,
                flavor=flavor,
                suppress_stdout=True
            )

            print(f"Found {len(tables)} tables")

            # Save each table
            extracted_tables = []
            for i, table in enumerate(tables):
                df = table.df
                # Skip empty tables
                if df.empty or len(df) < 2:
                    continue

                # Save to CSV
                output_file = self.output_dir / f"{self.filename}_camelot_{flavor}_table_{i+1}.csv"
                df.to_csv(output_file, index=False)
                print(f"  Table {i+1}: {df.shape[0]} rows x {df.shape[1]} cols -> {output_file.name}")
                extracted_tables.append(df)

            return extracted_tables

        except Exception as e:
            print(f"Error with Camelot: {e}")
            return None

    def extract_with_tabula(self, pages='all'):
        """Extract tables using Tabula"""
        if not TABULA_AVAILABLE:
            print("Tabula not available. Skipping.")
            return None

        print(f"\n{'='*60}")
        print(f"Extracting with Tabula...")
        print(f"{'='*60}")

        try:
            tables = tabula.read_pdf(
                self.pdf_path,
                pages=pages,
                multiple_tables=True,
                pandas_options={'header': None}
            )

            print(f"Found {len(tables)} tables")

            # Save each table
            extracted_tables = []
            for i, df in enumerate(tables):
                # Skip empty tables
                if df.empty or len(df) < 2:
                    continue

                # Save to CSV
                output_file = self.output_dir / f"{self.filename}_tabula_table_{i+1}.csv"
                df.to_csv(output_file, index=False)
                print(f"  Table {i+1}: {df.shape[0]} rows x {df.shape[1]} cols -> {output_file.name}")
                extracted_tables.append(df)

            return extracted_tables

        except Exception as e:
            print(f"Error with Tabula: {e}")
            return None

    def extract_with_pdfplumber(self, pages=None):
        """Extract tables using pdfplumber"""
        if not PDFPLUMBER_AVAILABLE:
            print("pdfplumber not available. Skipping.")
            return None

        print(f"\n{'='*60}")
        print(f"Extracting with pdfplumber...")
        print(f"{'='*60}")

        try:
            extracted_tables = []
            table_count = 0

            with pdfplumber.open(self.pdf_path) as pdf:
                pages_to_process = pages if pages else range(len(pdf.pages))

                for page_num in pages_to_process:
                    if isinstance(pages_to_process, range):
                        page = pdf.pages[page_num]
                        current_page = page_num + 1
                    else:
                        page = pdf.pages[page_num - 1]
                        current_page = page_num

                    tables = page.extract_tables()

                    for table in tables:
                        if not table or len(table) < 2:
                            continue

                        # Convert to DataFrame
                        df = pd.DataFrame(table[1:], columns=table[0])

                        table_count += 1
                        output_file = self.output_dir / f"{self.filename}_pdfplumber_table_{table_count}.csv"
                        df.to_csv(output_file, index=False)
                        print(f"  Page {current_page}, Table {table_count}: {df.shape[0]} rows x {df.shape[1]} cols -> {output_file.name}")
                        extracted_tables.append(df)

            print(f"Total tables found: {table_count}")
            return extracted_tables

        except Exception as e:
            print(f"Error with pdfplumber: {e}")
            return None

    def extract_all(self, pages='all', methods=['camelot_lattice', 'camelot_stream', 'tabula', 'pdfplumber']):
        """
        Extract using all available methods

        Args:
            pages: Pages to extract (default: 'all')
            methods: List of extraction methods to use
        """
        print(f"\n{'#'*60}")
        print(f"Processing: {self.filename}")
        print(f"{'#'*60}")

        results = {}

        if 'camelot_lattice' in methods and CAMELOT_AVAILABLE:
            results['camelot_lattice'] = self.extract_with_camelot(pages=pages, flavor='lattice')

        if 'camelot_stream' in methods and CAMELOT_AVAILABLE:
            results['camelot_stream'] = self.extract_with_camelot(pages=pages, flavor='stream')

        if 'tabula' in methods and TABULA_AVAILABLE:
            results['tabula'] = self.extract_with_tabula(pages=pages)

        if 'pdfplumber' in methods and PDFPLUMBER_AVAILABLE:
            # Convert 'all' to None for pdfplumber
            pdfplumber_pages = None if pages == 'all' else pages
            results['pdfplumber'] = self.extract_with_pdfplumber(pages=pdfplumber_pages)

        return results


def main():
    """Main execution function"""

    # Check if any library is available
    if not any([CAMELOT_AVAILABLE, TABULA_AVAILABLE, PDFPLUMBER_AVAILABLE]):
        print("\nERROR: No PDF extraction libraries available!")
        print("\nPlease install at least one of the following:")
        print("  pip install 'camelot-py[base]'")
        print("  pip install tabula-py")
        print("  pip install pdfplumber")
        sys.exit(1)

    # PDF directory
    data_dir = Path("Data")

    if not data_dir.exists():
        print(f"Error: {data_dir} directory not found!")
        sys.exit(1)

    # Get all PDF files
    pdf_files = sorted(data_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {data_dir}")
        sys.exit(1)

    print(f"\nFound {len(pdf_files)} PDF files:")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf.name} ({pdf.stat().st_size / 1024 / 1024:.1f} MB)")

    # For demonstration, extract from the smallest PDF (Part 7)
    target_pdf = data_dir / "SDS-31_Part7.pdf"

    if not target_pdf.exists():
        print(f"\nError: {target_pdf} not found!")
        sys.exit(1)

    print(f"\n{'*'*60}")
    print(f"Starting extraction from: {target_pdf.name}")
    print(f"{'*'*60}")

    # Create extractor
    extractor = SolubilityDataExtractor(str(target_pdf))

    # Extract from first 20 pages as a test
    # You can change this to 'all' to extract from all pages
    results = extractor.extract_all(pages='10-30')  # Test with pages 10-30

    print(f"\n{'*'*60}")
    print("Extraction Complete!")
    print(f"{'*'*60}")
    print(f"\nExtracted files saved to: {extractor.output_dir}/")
    print("\nNext steps:")
    print("1. Review the extracted CSV files")
    print("2. Identify which method gives the best results")
    print("3. Apply to all PDF files or specific page ranges")


if __name__ == "__main__":
    main()
