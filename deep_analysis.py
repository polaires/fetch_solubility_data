"""
Deep analysis of extracted solubility data
Identify data patterns and quality issues
"""

import pandas as pd
from pathlib import Path
import re
from collections import Counter

def improved_clean(value):
    """Improved OCR artifact cleaning"""
    if pd.isna(value):
        return value

    text = str(value)

    # Fix comma as decimal separator
    text = re.sub(r'(\d),(\d)', r'\1.\2', text)

    # Remove spaces in numbers
    text = re.sub(r'(\d)\s+\.', r'\1.', text)  # "0 . 015" -> "0.015"
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)  # "1 2" -> "12"
    text = re.sub(r'\.\s+(\d)', r'.\1', text)  # ". 5" -> ".5"

    # Common OCR fixes
    text = text.replace('mo1', 'mol')  # number 1 instead of letter l
    text = text.replace('pl!', 'pH')
    text = text.replace('I I', 'II')  # Roman numeral
    text = text.replace('t i', 'II')
    text = text.replace('l l', 'll')

    # Fix zero/o confusion
    text = re.sub(r'\bo\b', '0', text)  # standalone o -> 0
    text = re.sub(r'([^a-zA-Z])o([^a-zA-Z])', r'\g<1>0\g<2>', text)

    return text.strip()

def extract_numeric_data(df):
    """Try to extract numeric solubility data from table"""
    numeric_data = []

    for idx, row in df.iterrows():
        row_data = {}
        for col_idx, val in enumerate(row):
            val_str = improved_clean(val)

            # Try to parse as float
            try:
                # Look for numbers
                numbers = re.findall(r'\d+\.?\d*', val_str)
                if numbers:
                    row_data[f'col_{col_idx}'] = numbers
            except:
                pass

        if row_data:
            numeric_data.append(row_data)

    return numeric_data

def identify_table_type(df):
    """Identify what type of solubility data this table contains"""
    # Convert first few rows to string for analysis
    header_text = ' '.join([str(val) for val in df.iloc[:3].values.flatten() if pd.notna(val)]).lower()

    table_type = {
        'has_mass_percent': 'mass%' in header_text or 'mass  %' in header_text,
        'has_mol_percent': 'mol%' in header_text or 'mol  %' in header_text,
        'has_molality': 'mol/kg' in header_text or 'molkg' in header_text,
        'has_phase': 'phase' in header_text,
        'has_temp': 'temp' in header_text or '°c' in header_text or 'k' in header_text,
        'has_ratio': 'ratio' in header_text,
        'has_concentration': 'concentration' in header_text or 'conc' in header_text,
    }

    return table_type

def analyze_data_quality(csv_path):
    """Detailed quality analysis of a table"""
    df = pd.read_csv(csv_path)

    # Apply improved cleaning
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(improved_clean)

    table_type = identify_table_type(df)

    # Count data patterns
    patterns = {
        'decimal_numbers': 0,
        'integers': 0,
        'phase_labels': 0,
        'dashes': 0,
        'empty_cells': 0,
    }

    for val in df.values.flatten():
        if pd.isna(val):
            patterns['empty_cells'] += 1
        else:
            val_str = str(val)
            if re.match(r'^\d+\.\d+$', val_str):
                patterns['decimal_numbers'] += 1
            elif re.match(r'^\d+$', val_str):
                patterns['integers'] += 1
            elif val_str in ['A', 'B', 'C', 'D', 'E', 'F', 'II', 'III', 'A+B', 'B+C', 'D+E']:
                patterns['phase_labels'] += 1
            elif '---' in val_str or '----' in val_str:
                patterns['dashes'] += 1

    return {
        'file': csv_path.name,
        'rows': len(df),
        'cols': len(df.columns),
        'table_type': table_type,
        'patterns': patterns,
        'sample': df.head(3).to_dict('list'),
    }

def main():
    """Deep analysis of all data"""

    data_dir = Path("extracted_data")
    csv_files = sorted(data_dir.glob("*.csv"))

    print("="*80)
    print("DEEP DATA ANALYSIS")
    print("="*80)

    # Categorize tables by type
    categories = {
        'mass_percent_tables': [],
        'molality_tables': [],
        'phase_diagram_tables': [],
        'ratio_tables': [],
        'temperature_series': [],
        'other': [],
    }

    for csv_path in csv_files[:50]:  # Analyze first 50 in detail
        analysis = analyze_data_quality(csv_path)

        if analysis['table_type']['has_mass_percent'] and analysis['table_type']['has_molality']:
            categories['mass_percent_tables'].append(analysis)
        elif analysis['table_type']['has_molality']:
            categories['molality_tables'].append(analysis)
        elif analysis['table_type']['has_phase']:
            categories['phase_diagram_tables'].append(analysis)
        elif analysis['table_type']['has_ratio']:
            categories['ratio_tables'].append(analysis)
        elif analysis['table_type']['has_temp']:
            categories['temperature_series'].append(analysis)
        else:
            categories['other'].append(analysis)

    # Report findings
    print("\nTABLE CATEGORIZATION (first 50 files):")
    print("-" * 80)
    for cat_name, tables in categories.items():
        if tables:
            print(f"\n{cat_name.replace('_', ' ').title()}: {len(tables)} tables")
            if len(tables) <= 3:
                for t in tables:
                    print(f"  - {t['file']}: {t['rows']}x{t['cols']}, "
                          f"decimals={t['patterns']['decimal_numbers']}, "
                          f"phases={t['patterns']['phase_labels']}")

    # Find best quality tables
    print("\n" + "="*80)
    print("HIGH-QUALITY SOLUBILITY TABLES:")
    print("="*80)

    high_quality = []
    for csv_path in csv_files:
        analysis = analyze_data_quality(csv_path)

        # Quality score: many decimal numbers, has phase info, reasonable size
        score = (
            analysis['patterns']['decimal_numbers'] * 2 +
            analysis['patterns']['phase_labels'] * 5 +
            (10 if analysis['table_type']['has_mass_percent'] else 0) +
            (10 if analysis['table_type']['has_molality'] else 0) +
            (5 if analysis['table_type']['has_phase'] else 0) +
            (-1 * analysis['patterns']['dashes'])
        )

        if score > 50 and 5 < analysis['rows'] < 100:
            high_quality.append((score, analysis))

    # Show top 10
    high_quality.sort(key=lambda x: x[0], reverse=True)
    for score, analysis in high_quality[:10]:
        print(f"\n{analysis['file']} (score: {score})")
        print(f"  Size: {analysis['rows']}x{analysis['cols']}")
        print(f"  Type: {', '.join(k for k,v in analysis['table_type'].items() if v)}")
        print(f"  Data: {analysis['patterns']['decimal_numbers']} decimals, "
              f"{analysis['patterns']['phase_labels']} phase labels")

    # Show example of best table
    if high_quality:
        print("\n" + "="*80)
        print("EXAMPLE: Best Quality Table")
        print("="*80)
        best_file = data_dir / high_quality[0][1]['file']
        df = pd.read_csv(best_file)
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(improved_clean)

        print(f"\nFile: {best_file.name}")
        print(df.head(10).to_string(index=False, max_colwidth=12))

if __name__ == "__main__":
    main()
