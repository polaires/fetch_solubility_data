"""
Step 2.5: Identify chemical systems for each table

This script analyzes PDFs to extract chemical system information and creates
a mapping of table files to chemical systems (e.g., "Na3PO4-H2O").
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
import tabula
import pandas as pd


def extract_system_from_text(text: str) -> List[str]:
    """
    Extract chemical system identifiers from text.

    Patterns matched:
    - Na3PO4-H2O
    - MgHPO4-Na2HPO4-H2O
    - (NH4)2HPO4-H2O

    Args:
        text: Text to search for chemical systems

    Returns:
        List of chemical system strings
    """
    systems = set()

    # Pattern for chemical formulas with components separated by hyphens
    # Matches things like: Na3PO4-H2O, MgHPO4-Na2HPO4-H2O
    patterns = [
        # Full system pattern with H2O
        r'([A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\))?[A-Z][a-z0-9()]*(?:\s*[-–—]\s*[A-Z][a-z]?\d*(?:\([A-Z][a-z]?\d*\))?[A-Z][a-z0-9()]*)*\s*[-–—]\s*H\s*2?\s*O)',

        # Phosphate-specific patterns
        r'((?:Na|K|Mg|Ca|NH4|Li|Rb|Cs)\d*(?:H\d?)?\s*(?:PO4|P2O7|HPO4|H2PO4)(?:\s*[-–—]\s*(?:Na|K|Mg|Ca|NH4|Li|Rb|Cs|H)\d*(?:H\d?)?\s*(?:PO4|P2O7|HPO4|H2PO4|O))*\s*[-–—]\s*H\s*2?\s*O)',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            system = match.group(1).strip()
            # Clean up spacing
            system = re.sub(r'\s+', '', system)
            # Normalize H2O
            system = re.sub(r'H\s*2?\s*O', 'H2O', system)
            # Normalize hyphens
            system = re.sub(r'[–—]', '-', system)

            if 'H2O' in system:
                systems.add(system)

    return list(systems)


def identify_systems_in_pdf(pdf_path: Path, part_name: str) -> Dict[str, str]:
    """
    Identify chemical systems for all tables in a PDF.

    Strategy:
    1. Extract text from each page
    2. Look for chemical system patterns
    3. Associate systems with tables on that page
    4. Track page-to-page context

    Args:
        pdf_path: Path to PDF file
        part_name: Part name (e.g., "Part1")

    Returns:
        Dict mapping filename -> chemical system
    """
    import pdfplumber

    mapping = {}
    current_system = "Unknown"
    table_counter = 1

    print(f"\nProcessing {pdf_path.name}...")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Extract text from page
                text = page.extract_text() or ""

                # Count tables on this page
                tables = page.find_tables()
                num_tables = len(tables)

                # Look for chemical system in text
                systems_found = extract_system_from_text(text)

                if systems_found:
                    # Use the first system found (usually the main one)
                    current_system = systems_found[0]
                    print(f"  Page {page_num}: Found system '{current_system}' ({num_tables} tables)")

                # Assign current system to all tables on this page
                for _ in range(num_tables):
                    filename = f"SDS-31_{part_name}_table_{table_counter:03d}.csv"
                    mapping[filename] = current_system
                    table_counter += 1

    except Exception as e:
        print(f"  Warning: Could not process {pdf_path.name}: {e}")
        # Fallback: assign Unknown to expected number of tables
        # This is a rough estimate based on typical extraction

    return mapping


def create_system_mapping_tabula_fallback(data_dir: Path) -> Dict[str, Dict]:
    """
    Create system mapping using tabula-py (fallback method).

    This analyzes the text content of extracted tables to infer systems.
    Less accurate than PDF text extraction but works without pdfplumber.

    Args:
        data_dir: Directory containing PDFs

    Returns:
        Dict mapping filename -> {system, part, confidence}
    """
    mapping = {}
    pdf_files = sorted(data_dir.glob("SDS-31_Part*.pdf"))

    for pdf_file in pdf_files:
        # Extract part number
        match = re.search(r'Part(\d+)', pdf_file.name)
        if not match:
            continue

        part_name = f"Part{match.group(1)}"
        table_num = 1

        try:
            # Read PDF with tabula to get text context
            tables = tabula.read_pdf(
                str(pdf_file),
                pages='all',
                multiple_tables=True,
                pandas_options={'header': None}
            )

            current_system = "Unknown"

            for table in tables:
                # Convert table to string and search for chemical formulas
                table_text = table.to_string()
                systems = extract_system_from_text(table_text)

                if systems:
                    current_system = systems[0]

                filename = f"SDS-31_{part_name}_table_{table_num:03d}.csv"
                mapping[filename] = {
                    'system': current_system,
                    'part': part_name,
                    'table_num': table_num,
                    'confidence': 'high' if systems else 'low'
                }
                table_num += 1

        except Exception as e:
            print(f"Warning: Could not process {pdf_file.name} with tabula: {e}")

    return mapping


def save_system_mapping(mapping: Dict, output_path: Path):
    """Save chemical system mapping to JSON file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(mapping, f, indent=2)

    print(f"\n✓ Saved system mapping to {output_path}")

    # Print summary
    systems = {}
    for filename, info in mapping.items():
        system = info if isinstance(info, str) else info.get('system', 'Unknown')
        systems[system] = systems.get(system, 0) + 1

    print(f"\nChemical Systems Identified:")
    for system, count in sorted(systems.items(), key=lambda x: -x[1]):
        print(f"  {system}: {count} tables")


def identify_all_systems(data_dir: Path, output_path: Path, use_pdfplumber: bool = True) -> Dict:
    """
    Main function to identify chemical systems for all PDFs.

    Args:
        data_dir: Directory containing PDF files
        output_path: Path to save mapping JSON
        use_pdfplumber: Whether to use pdfplumber (more accurate) or tabula (fallback)

    Returns:
        System mapping dict
    """
    print("="*80)
    print("IDENTIFYING CHEMICAL SYSTEMS")
    print("="*80)

    if use_pdfplumber:
        try:
            import pdfplumber

            all_mapping = {}
            pdf_files = sorted(data_dir.glob("SDS-31_Part*.pdf"))

            for pdf_file in pdf_files:
                match = re.search(r'Part(\d+)', pdf_file.name)
                if match:
                    part_name = f"Part{match.group(1)}"
                    part_mapping = identify_systems_in_pdf(pdf_file, part_name)
                    all_mapping.update(part_mapping)

            # Convert to full format
            full_mapping = {}
            for filename, system in all_mapping.items():
                match = re.search(r'Part(\d+)_table_(\d+)', filename)
                if match:
                    full_mapping[filename] = {
                        'system': system,
                        'part': f"Part{match.group(1)}",
                        'table_num': int(match.group(2)),
                        'confidence': 'high' if system != 'Unknown' else 'low'
                    }

            mapping = full_mapping

        except ImportError:
            print("Warning: pdfplumber not available, using tabula fallback")
            mapping = create_system_mapping_tabula_fallback(data_dir)
    else:
        mapping = create_system_mapping_tabula_fallback(data_dir)

    save_system_mapping(mapping, output_path)

    return {
        'success': True,
        'total_tables': len(mapping),
        'mapping_file': str(output_path)
    }


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description='Identify chemical systems in PDF tables')
    parser.add_argument('--data-dir', type=Path, default=Path('Data'),
                      help='Directory containing PDF files')
    parser.add_argument('--output', type=Path,
                      default=Path('output/02_cleaned/chemical_systems.json'),
                      help='Output path for system mapping JSON')
    parser.add_argument('--method', choices=['pdfplumber', 'tabula'], default='tabula',
                      help='Method to use for system identification')

    args = parser.parse_args()

    use_pdfplumber = args.method == 'pdfplumber'
    result = identify_all_systems(args.data_dir, args.output, use_pdfplumber)

    if result['success']:
        print(f"\n✓ Successfully identified systems for {result['total_tables']} tables")
    else:
        print("\n✗ Failed to identify chemical systems")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
