"""
Generate comprehensive summary of extracted solubility data
Show what information is available across all PDFs
"""

import pandas as pd
from pathlib import Path
import re

def clean_value(val):
    """Final improved cleaning"""
    if pd.isna(val):
        return val

    text = str(val)

    # Fix decimal separators
    text = re.sub(r'(\d),(\d)', r'\1.\2', text)  # comma -> period

    # Remove spaces in numbers
    text = re.sub(r'(\d)\s+\.', r'\1.', text)
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    text = re.sub(r'\.\s+(\d)', r'.\1', text)

    # Fix common OCR errors
    text = text.replace('mo1', 'mol')
    text = text.replace('Q ', '0.')
    text = text.replace('a .', '0.')
    text = text.replace('a . so', '0.50')
    text = text.replace('Q .', '0.')
    text = text.replace('I I', 'II')
    text = text.replace('t i', 'II')

    # Fix zero confusion
    text = re.sub(r'\bQ\b', '0', text)
    text = re.sub(r'\ba\b', '0', text)

    return text.strip()

def summarize_table(csv_path):
    """Generate summary for one table"""
    df = pd.read_csv(csv_path)

    # Clean data
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_value)

    # Analyze content
    all_text = ' '.join([str(v) for v in df.values.flatten() if pd.notna(v)]).lower()

    return {
        'file': csv_path.name,
        'part': csv_path.stem.split('_')[1],
        'table_num': csv_path.stem.split('_')[-1],
        'rows': len(df),
        'cols': len(df.columns),
        'has_mass_percent': 'mass%' in all_text or 'mass  %' in all_text,
        'has_mol_percent': 'mol%' in all_text,
        'has_molality': 'mol/kg' in all_text or 'molkg' in all_text,
        'has_mole_fraction': 'mole fraction' in all_text or 'x(' in all_text,
        'has_phase_info': any(p in all_text for p in ['phase', ' a ', ' b ', ' c ', ' ii ', ' iii ']),
        'has_temperature': any(t in all_text for t in ['temp', '°c', '°k', 'k.']),
        'has_concentration': 'concentration' in all_text,
        'has_solubility': 'solubility' in all_text,
        'has_ratio': 'ratio' in all_text,
        'numeric_count': sum(1 for v in df.values.flatten()
                           if pd.notna(v) and re.search(r'\d+\.?\d*', str(v))),
    }

def main():
    """Generate comprehensive summary"""

    data_dir = Path("extracted_data")
    csv_files = sorted(data_dir.glob("*.csv"))

    print("="*80)
    print("COMPREHENSIVE DATA SUMMARY")
    print("="*80)
    print(f"Total files: {len(csv_files)}")

    # Analyze all files
    summaries = [summarize_table(f) for f in csv_files]

    # Overall statistics
    print("\n" + "="*80)
    print("DATA TYPES FOUND:")
    print("="*80)

    total_with = {
        'mass%': sum(1 for s in summaries if s['has_mass_percent']),
        'mol%': sum(1 for s in summaries if s['has_mol_percent']),
        'molality (mol/kg)': sum(1 for s in summaries if s['has_molality']),
        'mole fraction': sum(1 for s in summaries if s['has_mole_fraction']),
        'phase information': sum(1 for s in summaries if s['has_phase_info']),
        'temperature data': sum(1 for s in summaries if s['has_temperature']),
        'concentration': sum(1 for s in summaries if s['has_concentration']),
        'solubility': sum(1 for s in summaries if s['has_solubility']),
        'ratio data': sum(1 for s in summaries if s['has_ratio']),
    }

    for data_type, count in total_with.items():
        pct = count / len(summaries) * 100
        print(f"  {data_type:20s}: {count:3d} tables ({pct:5.1f}%)")

    # By part
    print("\n" + "="*80)
    print("DATA BY PDF PART:")
    print("="*80)

    from collections import defaultdict
    by_part = defaultdict(list)
    for s in summaries:
        by_part[s['part']].append(s)

    for part in sorted(by_part.keys()):
        part_summaries = by_part[part]
        total_rows = sum(s['rows'] for s in part_summaries)
        total_numeric = sum(s['numeric_count'] for s in part_summaries)
        avg_cols = sum(s['cols'] for s in part_summaries) / len(part_summaries)

        mass_pct = sum(1 for s in part_summaries if s['has_mass_percent'])
        mol_pct = sum(1 for s in part_summaries if s['has_molality'])
        phase_pct = sum(1 for s in part_summaries if s['has_phase_info'])

        print(f"\n{part}:")
        print(f"  Tables: {len(part_summaries)}")
        print(f"  Total rows: {total_rows:,}")
        print(f"  Total numeric values: {total_numeric:,}")
        print(f"  Avg columns: {avg_cols:.1f}")
        print(f"  With mass%: {mass_pct} ({mass_pct/len(part_summaries)*100:.0f}%)")
        print(f"  With molality: {mol_pct} ({mol_pct/len(part_summaries)*100:.0f}%)")
        print(f"  With phases: {phase_pct} ({phase_pct/len(part_summaries)*100:.0f}%)")

    # Find richest tables
    print("\n" + "="*80)
    print("RICHEST SOLUBILITY DATA TABLES (multi-parameter):")
    print("="*80)

    rich_tables = []
    for s in summaries:
        score = (
            (1 if s['has_mass_percent'] else 0) +
            (1 if s['has_molality'] else 0) +
            (1 if s['has_phase_info'] else 0) +
            (1 if s['has_temperature'] else 0) +
            (1 if s['has_mol_percent'] else 0)
        )
        if score >= 3:  # At least 3 types of data
            rich_tables.append((score, s))

    rich_tables.sort(key=lambda x: x[0], reverse=True)

    print(f"\nFound {len(rich_tables)} tables with 3+ data types:")
    for score, s in rich_tables[:15]:
        data_types = []
        if s['has_mass_percent']: data_types.append('mass%')
        if s['has_mol_percent']: data_types.append('mol%')
        if s['has_molality']: data_types.append('mol/kg')
        if s['has_phase_info']: data_types.append('phase')
        if s['has_temperature']: data_types.append('temp')

        print(f"  {s['file']:35s} ({s['rows']:2d}x{s['cols']:2d}): {', '.join(data_types)}")

    # Example of rich table
    if rich_tables:
        print("\n" + "="*80)
        print("EXAMPLE: Multi-Parameter Table")
        print("="*80)

        best_file = data_dir / rich_tables[0][1]['file']
        df = pd.read_csv(best_file)
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(clean_value)

        print(f"\nFile: {best_file.name}")
        print(f"Contains: {', '.join([k.replace('has_', '') for k, v in rich_tables[0][1].items() if k.startswith('has_') and v])}")
        print("\nFirst 8 rows:")
        print(df.head(8).to_string(index=False, max_colwidth=10))

    # Save summary
    print("\n" + "="*80)
    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv('extraction_summary.csv', index=False)
    print(f"✓ Full summary saved to extraction_summary.csv")

if __name__ == "__main__":
    main()
