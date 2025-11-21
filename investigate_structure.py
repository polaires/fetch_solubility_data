"""
Investigate table relationships and prepare for database structure
Understand what additional corrections are needed
"""

import pandas as pd
from pathlib import Path
import re
from collections import defaultdict

def extract_metadata_from_table(csv_path):
    """Extract metadata to understand table relationships"""
    df = pd.read_csv(csv_path)

    # Look for system information in first few rows
    system_info = {
        'file': csv_path.name,
        'part': csv_path.stem.split('_')[1],
        'table_num': int(csv_path.stem.split('_')[-1].replace('table', '')),
        'rows': len(df),
        'cols': len(df.columns),
    }

    # Check first 5 rows for chemical formulas and system identifiers
    header_text = ' '.join([str(v) for v in df.iloc[:5].values.flatten() if pd.notna(v)])

    # Look for chemical formulas
    chemicals = re.findall(r'\b[A-Z][a-z]?\d*[A-Z][a-z]?\d*\b', header_text)
    system_info['chemicals'] = list(set(chemicals))[:5]  # Limit to 5

    # Look for system identifiers
    if 'na' in header_text.lower() or 'sodium' in header_text.lower():
        system_info['element'] = 'Na'
    elif 'li' in header_text.lower() or 'lithium' in header_text.lower():
        system_info['element'] = 'Li'
    elif 'k' in header_text.lower() or 'potassium' in header_text.lower():
        system_info['element'] = 'K'

    # Check if this is a continuation table (starts with data, no header)
    first_val = str(df.iloc[0, 0])
    system_info['likely_continuation'] = bool(re.match(r'^\d+\.?\d*$', first_val))

    # Check for reference numbers or figure labels
    system_info['has_references'] = 'ref' in header_text.lower() or 'fig' in header_text.lower()

    return system_info

def analyze_table_sequences():
    """Analyze how tables relate to each other within each PDF"""

    data_dir = Path("extracted_data")
    csv_files = sorted(data_dir.glob("*.csv"))

    print("="*80)
    print("TABLE RELATIONSHIP ANALYSIS")
    print("="*80)

    # Group by PDF part
    by_part = defaultdict(list)
    for csv_path in csv_files:
        meta = extract_metadata_from_table(csv_path)
        by_part[meta['part']].append(meta)

    # Analyze each part
    for part in sorted(by_part.keys()):
        tables = sorted(by_part[part], key=lambda x: x['table_num'])

        print(f"\n{part}: {len(tables)} tables")
        print("-" * 80)

        # Look for table sequences (likely related tables)
        sequences = []
        current_seq = [tables[0]]

        for i in range(1, len(tables)):
            prev = tables[i-1]
            curr = tables[i]

            # Check if tables might be related:
            # - Sequential numbers
            # - Similar column counts
            # - Current is continuation (no header)
            if (curr['table_num'] == prev['table_num'] + 1 and
                abs(curr['cols'] - prev['cols']) <= 2):
                current_seq.append(curr)
            else:
                if len(current_seq) > 1:
                    sequences.append(current_seq)
                current_seq = [curr]

        if len(current_seq) > 1:
            sequences.append(current_seq)

        # Report sequences
        if sequences:
            print(f"\nPotential related table groups:")
            for seq in sequences:
                nums = [t['table_num'] for t in seq]
                cols = [t['cols'] for t in seq]
                rows_total = sum(t['rows'] for t in seq)
                print(f"  Tables {min(nums):03d}-{max(nums):03d}: {len(seq)} tables, "
                      f"{rows_total} total rows, {cols} columns")

def identify_issues():
    """Identify data quality issues that need correction"""

    data_dir = Path("cleaned_data")
    csv_files = sorted(data_dir.glob("*.csv"))[:30]  # Sample first 30

    print("\n" + "="*80)
    print("DATA QUALITY ISSUES TO FIX")
    print("="*80)

    issues = {
        'no_clear_header': [],
        'mixed_header_data': [],
        'multiple_subheaders': [],
        'merged_cells': [],
        'reference_numbers_in_data': [],
    }

    for csv_path in csv_files:
        df = pd.read_csv(csv_path)

        # Check if first row looks like header
        first_row = df.iloc[0].astype(str)
        has_numbers_in_first = sum(1 for v in first_row if re.search(r'\d+\.\d+', v))

        if has_numbers_in_first > len(first_row) / 2:
            issues['no_clear_header'].append(csv_path.name)

        # Check for mixed header/data in first 3 rows
        header_text = ' '.join([str(v) for v in df.iloc[:3].values.flatten()])
        if 'mass%' in header_text and 'temp' in header_text and re.search(r'\d+\.\d+', header_text):
            issues['mixed_header_data'].append(csv_path.name)

        # Check for merged cells (multiple values in one cell)
        for val in df.values.flatten():
            if pd.notna(val):
                val_str = str(val)
                # Look for patterns like "2.73 NaN"
                if re.search(r'\d+\.\d+\s+\w+', val_str):
                    issues['merged_cells'].append(csv_path.name)
                    break

        # Check for reference numbers in data columns
        for col in df.columns:
            col_vals = df[col].astype(str)
            # Look for patterns like "(D)" or "[1]" mixed with numbers
            if any(re.search(r'\d+\.\d+\s*[\(\[]', v) for v in col_vals):
                issues['reference_numbers_in_data'].append(csv_path.name)
                break

    print("\nIssues found:")
    for issue_type, files in issues.items():
        if files:
            print(f"\n{issue_type.replace('_', ' ').title()}: {len(files)} files")
            for f in files[:5]:
                print(f"  - {f}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")

def check_column_structure():
    """Analyze typical column structures"""

    print("\n" + "="*80)
    print("TYPICAL TABLE STRUCTURES")
    print("="*80)

    data_dir = Path("cleaned_data")

    # Sample some high-quality tables
    samples = [
        "SDS-31_Part1_table_033.csv",
        "SDS-31_Part2_table_046.csv",
        "SDS-31_Part2_table_017.csv",
    ]

    for fname in samples:
        fpath = data_dir / fname
        if not fpath.exists():
            continue

        df = pd.read_csv(fpath)
        print(f"\n{fname}:")
        print(f"  Columns: {df.shape[1]}, Rows: {df.shape[0]}")
        print(f"  First 3 rows:")
        for idx in range(min(3, len(df))):
            row_sample = [str(df.iloc[idx, i])[:15] for i in range(min(5, len(df.columns)))]
            print(f"    Row {idx}: {' | '.join(row_sample)}")

def main():
    """Run all analyses"""
    analyze_table_sequences()
    identify_issues()
    check_column_structure()

    print("\n" + "="*80)
    print("RECOMMENDATIONS FOR DATABASE PREPARATION")
    print("="*80)
    print("""
1. MERGE RELATED TABLES:
   - Identify table sequences from same chemical system
   - Concatenate data tables with same column structure
   - Preserve table boundaries with metadata

2. EXTRACT COLUMN HEADERS:
   - Parse first 2-3 rows to identify column names
   - Standardize column names (mass%, mol%, mol/kg, phase)
   - Remove header rows from data

3. SEPARATE METADATA:
   - Extract chemical system info (compounds, ratios)
   - Extract temperature information
   - Extract references and notes
   - Store separately from numeric data

4. CLEAN DATA VALUES:
   - Remove reference markers from values (e.g., "0.026 (D)" -> 0.026)
   - Split merged cells
   - Convert all numeric strings to floats
   - Handle missing data (----, NaN)

5. ADD IDENTIFIERS:
   - Add PDF source (Part1-7)
   - Add table number
   - Add system identifier (e.g., "Na3PO4-H2O")
   - Add temperature (if available)

6. VALIDATE:
   - Check numeric ranges (0-100 for mass%)
   - Verify phase labels are valid
   - Check for duplicate data
    """)

if __name__ == "__main__":
    main()
