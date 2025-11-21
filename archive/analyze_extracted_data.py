"""
Analyze extracted solubility data for consistency and quality
Clean OCR artifacts and check data structure
"""

import pandas as pd
from pathlib import Path
import re
from collections import defaultdict

def clean_ocr_artifacts(value):
    """Clean OCR artifacts from text values"""
    if pd.isna(value):
        return value

    # Convert to string
    text = str(value)

    # Remove spaces within numbers (e.g., "0 . 015" -> "0.015", "1 2 3" -> "123")
    # Pattern: digit, space, optional more (digit/space/.), space, digit
    cleaned = re.sub(r'(\d)\s+\.', r'\1.', text)  # "0 . 015" -> "0.015"
    cleaned = re.sub(r'(\d)\s+(\d)', r'\1\2', cleaned)  # "1 2" -> "12"
    cleaned = re.sub(r'\.\s+(\d)', r'.\1', cleaned)  # ". 5" -> ".5"

    # Remove spaces around commas
    cleaned = re.sub(r'\s*,\s*', ',', cleaned)

    # Clean common OCR errors
    cleaned = cleaned.replace('o . ', '0.')  # lowercase o instead of zero
    cleaned = cleaned.replace('O . ', '0.')
    cleaned = cleaned.replace('l ', '1')  # lowercase L instead of 1

    return cleaned.strip()

def analyze_table(csv_path):
    """Analyze a single table for structure and data quality"""
    try:
        df = pd.read_csv(csv_path)

        # Clean all string columns
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(clean_ocr_artifacts)

        info = {
            'file': csv_path.name,
            'rows': len(df),
            'cols': len(df.columns),
            'has_mass_percent': any('mass' in str(col).lower() or
                                   any('mass' in str(val).lower() for val in df.iloc[:2].values.flatten() if pd.notna(val))
                                   for col in df.columns),
            'has_mol': any('mol' in str(col).lower() or
                          any('mol' in str(val).lower() for val in df.iloc[:2].values.flatten() if pd.notna(val))
                          for col in df.columns),
            'has_phase': any('phase' in str(col).lower() or
                           any('phase' in str(val).lower() for val in df.iloc[:2].values.flatten() if pd.notna(val))
                           for col in df.columns),
            'has_temp': any('temp' in str(val).lower() for val in df.values.flatten() if pd.notna(val)),
            'numeric_cols': sum(1 for col in df.columns if df[col].dtype in ['float64', 'int64']),
            'sample_data': df.head(3).to_dict('records') if len(df) <= 10 else None,
        }

        return info, df

    except Exception as e:
        return {'file': csv_path.name, 'error': str(e)}, None

def main():
    """Analyze all extracted data"""

    data_dir = Path("extracted_data")
    csv_files = sorted(data_dir.glob("*.csv"))

    print(f"Analyzing {len(csv_files)} CSV files...")
    print("="*80)

    # Statistics
    stats = {
        'total_files': len(csv_files),
        'total_rows': 0,
        'files_with_mass_percent': 0,
        'files_with_mol': 0,
        'files_with_phase': 0,
        'files_with_temp': 0,
        'column_distribution': defaultdict(int),
        'errors': [],
    }

    # Analyze each part
    parts = defaultdict(list)

    for csv_path in csv_files:
        info, df = analyze_table(csv_path)

        if 'error' in info:
            stats['errors'].append(info)
            continue

        # Update statistics
        stats['total_rows'] += info['rows']
        if info['has_mass_percent']:
            stats['files_with_mass_percent'] += 1
        if info['has_mol']:
            stats['files_with_mol'] += 1
        if info['has_phase']:
            stats['files_with_phase'] += 1
        if info['has_temp']:
            stats['files_with_temp'] += 1
        stats['column_distribution'][info['cols']] += 1

        # Group by part
        part = csv_path.stem.split('_')[1]  # e.g., "Part1"
        parts[part].append(info)

    # Print summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total files: {stats['total_files']}")
    print(f"Total rows: {stats['total_rows']:,}")
    print(f"\nData Content:")
    print(f"  Files with mass%: {stats['files_with_mass_percent']} ({stats['files_with_mass_percent']/stats['total_files']*100:.1f}%)")
    print(f"  Files with mol data: {stats['files_with_mol']} ({stats['files_with_mol']/stats['total_files']*100:.1f}%)")
    print(f"  Files with phase info: {stats['files_with_phase']} ({stats['files_with_phase']/stats['total_files']*100:.1f}%)")
    print(f"  Files with temperature: {stats['files_with_temp']} ({stats['files_with_temp']/stats['total_files']*100:.1f}%)")

    print(f"\nColumn Distribution:")
    for cols, count in sorted(stats['column_distribution'].items()):
        print(f"  {cols} columns: {count} files")

    print(f"\n" + "="*80)
    print("BY PART:")
    print("="*80)
    for part in sorted(parts.keys()):
        part_info = parts[part]
        total_rows = sum(info['rows'] for info in part_info)
        avg_cols = sum(info['cols'] for info in part_info) / len(part_info)
        print(f"\n{part}: {len(part_info)} tables, {total_rows:,} rows, avg {avg_cols:.1f} columns")

    # Show sample tables
    print(f"\n" + "="*80)
    print("SAMPLE TABLES (first 5 with data):")
    print("="*80)

    sample_count = 0
    for csv_path in csv_files[:20]:  # Check first 20
        info, df = analyze_table(csv_path)
        if 'error' in info or df is None:
            continue

        if info['has_mass_percent'] or info['has_mol']:
            print(f"\n{info['file']} ({info['rows']} rows × {info['cols']} cols)")
            print("-" * 80)
            print(df.head(5).to_string(index=False, max_colwidth=15))
            sample_count += 1

            if sample_count >= 5:
                break

    # Save cleaned data summary
    print(f"\n" + "="*80)
    print("CLEANING RESULTS:")
    print("="*80)

    # Create cleaned directory
    cleaned_dir = Path("cleaned_data")
    cleaned_dir.mkdir(exist_ok=True)

    cleaned_count = 0
    for csv_path in csv_files:
        info, df = analyze_table(csv_path)
        if df is not None:
            # Save cleaned version
            output_path = cleaned_dir / csv_path.name
            df.to_csv(output_path, index=False)
            cleaned_count += 1

    print(f"✓ Cleaned {cleaned_count} files saved to {cleaned_dir}/")

    if stats['errors']:
        print(f"\n⚠ Errors in {len(stats['errors'])} files:")
        for err in stats['errors'][:5]:
            print(f"  {err['file']}: {err['error']}")

if __name__ == "__main__":
    main()
