"""
Step 3: Clean extracted data and fix OCR artifacts

This script cleans OCR artifacts from extracted tables and standardizes values.
"""

import pandas as pd
from pathlib import Path
import argparse
import json
from typing import Dict, List
from utils import advanced_clean, ensure_directory, count_numeric_values


def clean_table(csv_path: Path) -> tuple[pd.DataFrame, Dict]:
    """
    Clean a single table by applying OCR artifact fixes

    Args:
        csv_path: Path to CSV file

    Returns:
        Tuple of (cleaned DataFrame, metadata dict)
    """
    df = pd.read_csv(csv_path)

    # Count before cleaning
    original_numeric = count_numeric_values(df)

    # Apply cleaning to all columns
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].map(advanced_clean)

    # Count after cleaning
    cleaned_numeric = count_numeric_values(df)

    metadata = {
        'file': csv_path.name,
        'rows': len(df),
        'cols': len(df.columns),
        'original_numeric': original_numeric,
        'cleaned_numeric': cleaned_numeric,
    }

    return df, metadata


def clean_all_tables(input_dir: Path, output_dir: Path) -> Dict:
    """
    Clean all tables in input directory

    Args:
        input_dir: Directory with raw extracted CSVs
        output_dir: Directory to save cleaned CSVs

    Returns:
        Summary dict with cleaning results
    """
    ensure_directory(output_dir)

    csv_files = sorted(input_dir.glob("*.csv"))

    # Skip manifest files
    csv_files = [f for f in csv_files if 'manifest' not in f.name.lower() and 'summary' not in f.name.lower()]

    if not csv_files:
        print(f"No CSV files found in {input_dir}")
        return {'success': False, 'files': 0}

    print("="*80)
    print(f"CLEANING {len(csv_files)} TABLES")
    print("="*80)

    results = []
    total_numeric_before = 0
    total_numeric_after = 0

    for csv_path in csv_files:
        try:
            df_clean, metadata = clean_table(csv_path)

            # Save cleaned table
            output_path = output_dir / csv_path.name
            df_clean.to_csv(output_path, index=False)

            results.append(metadata)
            total_numeric_before += metadata['original_numeric']
            total_numeric_after += metadata['cleaned_numeric']

            if (len(results)) % 50 == 0:
                print(f"  Processed {len(results)}/{len(csv_files)} files...")

        except Exception as e:
            print(f"  ✗ Error cleaning {csv_path.name}: {e}")

    # Summary
    print("\n" + "="*80)
    print("CLEANING SUMMARY")
    print("="*80)
    print(f"Files processed: {len(results)}")
    print(f"Numeric values before: {total_numeric_before:,}")
    print(f"Numeric values after: {total_numeric_after:,}")
    print(f"Improvement: {total_numeric_after - total_numeric_before:+,} values")
    print(f"Output directory: {output_dir}")

    summary = {
        'success': True,
        'files_processed': len(results),
        'total_numeric_before': total_numeric_before,
        'total_numeric_after': total_numeric_after,
        'results': results,
    }

    # Save cleaning manifest
    manifest_path = output_dir / "cleaning_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n✓ Cleaning manifest saved: {manifest_path}")

    return summary


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Clean extracted tables and fix OCR artifacts"
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path('output/01_extracted'),
        help='Input directory with extracted CSVs (default: output/01_extracted/)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('output/02_cleaned'),
        help='Output directory for cleaned CSVs (default: output/02_cleaned/)'
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input directory not found: {args.input}")
        return

    summary = clean_all_tables(args.input, args.output)

    if summary['success']:
        print(f"\n✓ Cleaning complete: {summary['files_processed']} files processed")


if __name__ == "__main__":
    main()
