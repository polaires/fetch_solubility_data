#!/usr/bin/env python3
"""
Extract chemical system information from PDFs and create mapping to CSV tables.

This script parses the PDF text to find chemical system names (e.g., "Na3PO4-H2O")
and associates them with the extracted table numbers.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
import pdfplumber


def extract_text_with_tables(pdf_path: Path) -> List[Dict]:
    """
    Extract text and table positions from PDF.
    Returns list of {page, text, tables} dictionaries.
    """
    pages_data = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            tables = page.find_tables()

            pages_data.append({
                'page': page_num,
                'text': text,
                'num_tables': len(tables)
            })

    return pages_data


def find_chemical_systems(text: str) -> List[str]:
    """
    Extract chemical system names from text.

    Patterns to match:
    - "Na3PO4-H2O"
    - "MgHPO4-Na2HPO4-H2O"
    - "K2HPO4-KH2PO4-H2O"
    etc.
    """
    patterns = [
        # Pattern 1: Chemical formula with hyphens (most common)
        r'([A-Z][a-z]?\d*[A-Z][A-Za-z0-9]*(?:-[A-Z][a-z]?\d*[A-Z][A-Za-z0-9]*)+)',

        # Pattern 2: System with "system" keyword
        r'([A-Z][a-z]?\d*[A-Z][A-Za-z0-9]*(?:\s*[-–]\s*[A-Z][a-z]?\d*[A-Z][A-Za-z0-9]*)+)\s+system',

        # Pattern 3: Phosphate systems (specific to SDS-31)
        r'((?:Na|K|Mg|Ca|NH4)\d*(?:H|HP)?(?:PO4|P2O7)(?:\s*[-–]\s*(?:Na|K|Mg|Ca|NH4|H)\d*(?:H|HP)?(?:PO4|P2O7|O))*\s*[-–]\s*H\s*2?\s*O)',
    ]

    systems = set()
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            system = match.group(1).strip()
            # Clean up spaces in system name
            system = re.sub(r'\s+', '', system)
            # Ensure ends with H2O
            if 'H2O' in system or 'H O' in system:
                system = system.replace('H O', 'H2O')
                systems.add(system)

    return list(systems)


def map_tables_to_systems(pdf_path: Path, part_name: str) -> Dict[str, str]:
    """
    Create mapping of table filenames to chemical systems.

    Returns:
        Dict mapping "SDS-31_Part1_table_001.csv" -> "Na3PO4-H2O"
    """
    pages_data = extract_text_with_tables(pdf_path)

    mapping = {}
    current_system = "Unknown"
    table_counter = 1

    for page_data in pages_data:
        text = page_data['text']
        num_tables = page_data['num_tables']

        # Look for chemical system names on this page
        systems = find_chemical_systems(text)
        if systems:
            # Use the first (usually only) system found
            current_system = systems[0]

        # Assign current system to all tables on this page
        for _ in range(num_tables):
            filename = f"SDS-31_{part_name}_table_{table_counter:03d}.csv"
            mapping[filename] = current_system
            table_counter += 1

    return mapping


def create_full_mapping() -> Dict[str, Dict]:
    """
    Create full mapping for all PDFs.

    Returns:
        Dict mapping filename -> {system, part, table_num, page_hint}
    """
    data_dir = Path("Data")
    full_mapping = {}

    # Process each PDF part
    pdf_files = sorted(data_dir.glob("SDS-31_Part*.pdf"))

    for pdf_file in pdf_files:
        # Extract part number (e.g., "Part1")
        match = re.search(r'Part(\d+)', pdf_file.name)
        if not match:
            continue

        part_name = f"Part{match.group(1)}"
        print(f"Processing {pdf_file.name}...")

        try:
            part_mapping = map_tables_to_systems(pdf_file, part_name)

            for filename, system in part_mapping.items():
                # Parse table number
                table_match = re.search(r'table_(\d+)', filename)
                table_num = int(table_match.group(1)) if table_match else 0

                full_mapping[filename] = {
                    'system': system,
                    'part': part_name,
                    'table_num': table_num,
                    'pdf_source': pdf_file.name
                }

            print(f"  ✓ Mapped {len(part_mapping)} tables")

        except Exception as e:
            print(f"  ✗ Error processing {pdf_file.name}: {e}")

    return full_mapping


def main():
    """Main execution function."""
    print("Extracting chemical system information from PDFs...\n")

    # Create mapping
    mapping = create_full_mapping()

    # Save to JSON
    output_file = Path("web-interface/public/data/chemical_systems.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(mapping, f, indent=2)

    print(f"\n✓ Saved mapping to {output_file}")
    print(f"✓ Mapped {len(mapping)} tables")

    # Print summary by system
    systems = {}
    for filename, info in mapping.items():
        system = info['system']
        systems[system] = systems.get(system, 0) + 1

    print(f"\nChemical Systems Found ({len(systems)} unique):")
    for system, count in sorted(systems.items(), key=lambda x: -x[1]):
        print(f"  {system}: {count} tables")


if __name__ == '__main__':
    main()
