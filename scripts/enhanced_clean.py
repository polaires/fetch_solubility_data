"""
Enhanced Cleaning Script - Integrates all improvements

This script performs comprehensive data cleaning and enhancement:
1. OCR artifact cleaning
2. Phase marker extraction
3. Column type detection and standardization
4. Chemical system association
"""

import pandas as pd
from pathlib import Path
import argparse
import json
from typing import Dict, List, Tuple

# Import our enhancement modules
from utils import advanced_clean, ensure_directory, count_numeric_values
from phase_extractor import PhaseExtractor
from column_standardizer import ColumnStandardizer


def load_chemical_systems(systems_file: Path) -> Dict:
    """Load chemical systems mapping from JSON"""
    if systems_file.exists():
        with open(systems_file) as f:
            return json.load(f)
    return {}


def enhanced_clean_table(
    csv_path: Path,
    chemical_systems: Dict = None,
    extract_phases: bool = True,
    standardize_columns: bool = True
) -> Tuple[pd.DataFrame, Dict]:
    """
    Perform enhanced cleaning on a table.

    Args:
        csv_path: Path to CSV file
        chemical_systems: Dict mapping filenames to chemical systems
        extract_phases: Whether to extract phase markers
        standardize_columns: Whether to standardize column names

    Returns:
        Tuple of (cleaned DataFrame, metadata dict)
    """
    # Step 1: Load data
    df = pd.read_csv(csv_path)
    filename = csv_path.name

    metadata = {
        'file': filename,
        'original_rows': len(df),
        'original_cols': len(df.columns),
    }

    # Step 2: OCR cleaning (existing functionality)
    original_numeric = count_numeric_values(df)

    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].map(advanced_clean)

    cleaned_numeric = count_numeric_values(df)

    metadata['ocr_cleaning'] = {
        'original_numeric': original_numeric,
        'cleaned_numeric': cleaned_numeric,
        'improvement': cleaned_numeric - original_numeric
    }

    # Step 3: Phase extraction
    if extract_phases:
        extractor = PhaseExtractor()
        df = extractor.process_dataframe(df, numeric_only=True)
        unique_phases = extractor.get_unique_phases(df)

        metadata['phase_extraction'] = {
            'phases_found': list(unique_phases),
            'phase_columns_added': sum(1 for col in df.columns if '_phase' in col)
        }

    # Step 4: Column standardization
    if standardize_columns:
        standardizer = ColumnStandardizer()
        analysis = standardizer.analyze_table(df)

        # Store column metadata but don't rename yet
        # (keep original names for compatibility, add metadata for UI)
        metadata['column_analysis'] = {
            'types_detected': {
                col: info['detected_type']
                for col, info in analysis['columns'].items()
            },
            'standard_names': {
                col: info['standard_name']
                for col, info in analysis['columns'].items()
            },
            'summary': analysis['summary']
        }

    # Step 5: Add chemical system info
    if chemical_systems and filename in chemical_systems:
        system_info = chemical_systems[filename]
        metadata['chemical_system'] = system_info.get('system', 'Unknown')
        metadata['system_confidence'] = system_info.get('confidence', 'low')
    else:
        metadata['chemical_system'] = 'Unknown'
        metadata['system_confidence'] = 'none'

    # Final metadata
    metadata['final_rows'] = len(df)
    metadata['final_cols'] = len(df.columns)

    return df, metadata


def enhanced_clean_all(
    input_dir: Path,
    output_dir: Path,
    systems_file: Path = None,
    extract_phases: bool = True,
    standardize_columns: bool = True
) -> Dict:
    """
    Enhanced cleaning for all tables.

    Args:
        input_dir: Directory with raw extracted CSVs
        output_dir: Directory to save enhanced CSVs
        systems_file: Path to chemical systems JSON
        extract_phases: Whether to extract phase markers
        standardize_columns: Whether to standardize columns

    Returns:
        Summary dict with cleaning results
    """
    ensure_directory(output_dir)
    ensure_directory(output_dir / 'metadata')

    # Load chemical systems
    chemical_systems = {}
    if systems_file and systems_file.exists():
        chemical_systems = load_chemical_systems(systems_file)
        print(f"✓ Loaded {len(chemical_systems)} chemical system mappings")

    csv_files = sorted(input_dir.glob("*.csv"))
    csv_files = [f for f in csv_files if 'manifest' not in f.name.lower()]

    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return {'success': False, 'files': 0}

    print("="*80)
    print(f"ENHANCED CLEANING: {len(csv_files)} TABLES")
    print("="*80)
    print(f"Features enabled:")
    print(f"  • OCR cleaning: ✓")
    print(f"  • Phase extraction: {'✓' if extract_phases else '✗'}")
    print(f"  • Column standardization: {'✓' if standardize_columns else '✗'}")
    print(f"  • Chemical systems: {'✓' if chemical_systems else '✗'}")
    print()

    results = []
    systems_found = {}

    for i, csv_path in enumerate(csv_files, 1):
        try:
            print(f"[{i}/{len(csv_files)}] {csv_path.name}...", end=" ")

            # Enhanced cleaning
            df_clean, metadata = enhanced_clean_table(
                csv_path,
                chemical_systems=chemical_systems,
                extract_phases=extract_phases,
                standardize_columns=standardize_columns
            )

            # Save cleaned CSV
            output_path = output_dir / csv_path.name
            df_clean.to_csv(output_path, index=False)

            # Save metadata
            metadata_path = output_dir / 'metadata' / f"{csv_path.stem}_metadata.json"
            with open(metadata_path, 'w') as f:
                # Convert numpy types to Python types for JSON
                def convert_types(obj):
                    if hasattr(obj, 'item'):  # numpy types
                        return obj.item()
                    return obj

                json.dump(metadata, f, indent=2, default=convert_types)

            # Track systems
            if metadata.get('chemical_system') != 'Unknown':
                system = metadata['chemical_system']
                systems_found[system] = systems_found.get(system, 0) + 1

            results.append(metadata)
            print(f"✓ (system: {metadata.get('chemical_system', 'Unknown')})")

        except Exception as e:
            print(f"✗ Error: {e}")
            results.append({'file': csv_path.name, 'error': str(e)})

    # Create summary
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)

    successful = sum(1 for r in results if 'error' not in r)
    total_phases = sum(len(r.get('phase_extraction', {}).get('phases_found', []))
                      for r in results if 'phase_extraction' in r)

    print(f"Successfully processed: {successful}/{len(csv_files)} files")
    print(f"Total unique phase labels: {total_phases}")

    if systems_found:
        print(f"\nChemical systems identified: {len(systems_found)}")
        for system, count in sorted(systems_found.items(), key=lambda x: -x[1])[:10]:
            print(f"  {system}: {count} tables")

    summary = {
        'success': True,
        'total_files': len(csv_files),
        'successful': successful,
        'systems_identified': len(systems_found),
        'total_phase_labels': total_phases,
        'output_dir': str(output_dir),
    }

    # Save overall summary
    summary_path = output_dir / 'enhanced_cleaning_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Summary saved to {summary_path}")

    return summary


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description='Enhanced table cleaning with phase extraction and column standardization')
    parser.add_argument('--input-dir', type=Path, default=Path('output/01_extracted'),
                      help='Directory with raw extracted CSVs')
    parser.add_argument('--output-dir', type=Path, default=Path('output/02_cleaned_enhanced'),
                      help='Directory to save enhanced CSVs')
    parser.add_argument('--systems-file', type=Path,
                      default=Path('output/02_cleaned/chemical_systems.json'),
                      help='Path to chemical systems JSON')
    parser.add_argument('--no-phases', action='store_true',
                      help='Disable phase extraction')
    parser.add_argument('--no-standardize', action='store_true',
                      help='Disable column standardization')

    args = parser.parse_args()

    result = enhanced_clean_all(
        args.input_dir,
        args.output_dir,
        systems_file=args.systems_file,
        extract_phases=not args.no_phases,
        standardize_columns=not args.no_standardize
    )

    if result['success']:
        print(f"\n✓ Successfully enhanced {result['successful']} tables")
        return 0
    else:
        print("\n✗ Enhanced cleaning failed")
        return 1


if __name__ == '__main__':
    exit(main())
