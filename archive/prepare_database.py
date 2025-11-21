"""
Prepare cleaned, structured data ready for database import
- Merge related tables from same system
- Extract and standardize column headers
- Remove reference markers
- Validate data
- Create database-ready format
"""

import pandas as pd
from pathlib import Path
import re
import json

def advanced_clean(value):
    """Advanced cleaning for database preparation"""
    if pd.isna(value):
        return None

    text = str(value)

    # Remove reference markers but keep the value
    # "0.026 (D)" -> "0.026", marker="D"
    match = re.match(r'([0-9.]+)\s*[\(\[]([A-Z][\w.]*?)[\)\]]', text)
    if match:
        return match.group(1)  # Return just the number

    # Fix decimal separators
    text = re.sub(r'(\d),(\d)', r'\1.\2', text)

    # Remove spaces in numbers
    text = re.sub(r'(\d)\s+\.', r'\1.', text)
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    text = re.sub(r'\.\s+(\d)', r'.\1', text)

    # Common OCR fixes
    text = text.replace('mo1', 'mol')
    text = text.replace('Q .', '0.')
    text = text.replace('a .', '0.')
    text = text.replace('I I', 'II')
    text = text.replace('0. so', '0.50')
    text = text.replace('. so', '.50')

    # Fix specific patterns
    text = re.sub(r'\bs\s*o\b', '50', text)  # "s o" -> "50"
    text = re.sub(r'\b0\s*\.\s*s\s*o\b', '0.50', text)

    return text.strip()

def extract_phase_marker(value):
    """Extract phase label from value like '0.026 (D)'"""
    if pd.isna(value):
        return None

    text = str(value)
    match = re.search(r'[\(\[]([A-Z][\w.]*?)[\)\]]', text)
    if match:
        return match.group(1)
    return None

def parse_column_header(df, max_header_rows=3):
    """Parse first few rows to identify column headers"""
    headers = []

    for col_idx in range(len(df.columns)):
        # Collect potential header text from first few rows
        header_parts = []
        for row_idx in range(min(max_header_rows, len(df))):
            val = df.iloc[row_idx, col_idx]
            if pd.notna(val):
                val_str = str(val).strip()
                # Check if it looks like a header (contains text, not just numbers)
                if not re.match(r'^[\d\s.,]+$', val_str):
                    header_parts.append(val_str)

        # Combine header parts
        if header_parts:
            header = ' '.join(header_parts[:2])  # Use first 2 parts
        else:
            header = f'col_{col_idx}'

        headers.append(header)

    return headers

def identify_data_start_row(df):
    """Find where actual numeric data starts"""
    for row_idx in range(min(5, len(df))):
        row = df.iloc[row_idx]
        # Count numeric values
        numeric_count = sum(1 for v in row if pd.notna(v) and re.match(r'^[\d.,\s]+$', str(v)))

        # If >50% of columns are numeric, this is likely data
        if numeric_count > len(row) * 0.5:
            return row_idx

    return 0  # Default to first row

def process_table(csv_path):
    """Process a single table into database-ready format"""
    df_raw = pd.read_csv(csv_path)

    # Extract metadata
    metadata = {
        'source_file': csv_path.name,
        'pdf_part': csv_path.stem.split('_')[1],
        'table_num': int(csv_path.stem.split('_')[-1].replace('table', '')),
        'original_rows': len(df_raw),
        'original_cols': len(df_raw.columns),
    }

    # Parse headers
    headers = parse_column_header(df_raw)
    data_start = identify_data_start_row(df_raw)

    # Extract data rows (skip header rows)
    df_data = df_raw.iloc[data_start:].copy()
    df_data.columns = headers

    # Clean all values
    for col in df_data.columns:
        df_data[col] = df_data[col].map(advanced_clean)

    # Try to identify column types
    col_types = {}
    for col in headers:
        col_lower = col.lower()
        if 'mass%' in col_lower or 'mass  %' in col_lower:
            col_types[col] = 'mass_percent'
        elif 'mol%' in col_lower or 'mol  %' in col_lower:
            col_types[col] = 'mol_percent'
        elif 'mol/kg' in col_lower or 'molkg' in col_lower:
            col_types[col] = 'molality'
        elif 'phase' in col_lower:
            col_types[col] = 'phase'
        elif 'temp' in col_lower:
            col_types[col] = 'temperature'
        else:
            col_types[col] = 'unknown'

    metadata['column_types'] = col_types

    return df_data, metadata

def merge_table_sequence(csv_paths):
    """Merge a sequence of related tables"""
    all_data = []
    all_metadata = []

    for csv_path in csv_paths:
        df_data, metadata = process_table(csv_path)

        # Make column names unique by adding table number suffix if needed
        # Check for duplicate columns
        if len(df_data.columns) != len(set(df_data.columns)):
            # Has duplicates, make unique
            new_cols = []
            col_counts = {}
            for col in df_data.columns:
                if col in col_counts:
                    col_counts[col] += 1
                    new_cols.append(f"{col}_{col_counts[col]}")
                else:
                    col_counts[col] = 0
                    new_cols.append(col)
            df_data.columns = new_cols

        all_data.append(df_data)
        all_metadata.append(metadata)

    # Concatenate data - first align columns
    # Get all unique columns
    all_columns = set()
    for df in all_data:
        all_columns.update(df.columns)

    # Add missing columns to each dataframe
    for i, df in enumerate(all_data):
        for col in all_columns:
            if col not in df.columns:
                df[col] = None
        # Reorder columns consistently
        all_data[i] = df[sorted(df.columns)]

    # Now concatenate
    merged_df = pd.concat(all_data, ignore_index=True)

    # Combined metadata
    combined_meta = {
        'source_files': [m['source_file'] for m in all_metadata],
        'pdf_part': all_metadata[0]['pdf_part'],
        'table_range': f"{all_metadata[0]['table_num']:03d}-{all_metadata[-1]['table_num']:03d}",
        'total_rows': len(merged_df),
        'original_tables': len(all_metadata),
    }

    return merged_df, combined_meta

def create_database_ready_format():
    """Create final database-ready CSV with all necessary columns"""

    data_dir = Path("cleaned_data")

    print("="*80)
    print("PREPARING DATABASE-READY FORMAT")
    print("="*80)

    # Process first few tables as examples
    sample_tables = [
        "SDS-31_Part1_table_033.csv",
        "SDS-31_Part2_table_046.csv",
        "SDS-31_Part1_table_004.csv",
    ]

    output_dir = Path("database_ready")
    output_dir.mkdir(exist_ok=True)

    for fname in sample_tables:
        fpath = data_dir / fname
        if not fpath.exists():
            continue

        print(f"\nProcessing {fname}...")

        df_clean, metadata = process_table(fpath)

        # Save cleaned data
        output_path = output_dir / fname
        df_clean.to_csv(output_path, index=False)

        # Save metadata
        meta_path = output_dir / fname.replace('.csv', '_metadata.json')
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"  Cleaned: {len(df_clean)} rows, {len(df_clean.columns)} columns")
        print(f"  Column types: {metadata['column_types']}")
        print(f"  Saved to: {output_path.name}")

        # Show sample
        print(f"  Sample (first 3 rows):")
        print(df_clean.head(3).to_string(index=False, max_colwidth=12))

    print(f"\n✓ Database-ready files saved to {output_dir}/")

def demonstrate_table_merging():
    """Demonstrate merging a complete table sequence"""
    data_dir = Path("cleaned_data")
    output_dir = Path("database_ready")
    output_dir.mkdir(exist_ok=True)

    print("\n" + "="*80)
    print("DEMONSTRATING TABLE SEQUENCE MERGING")
    print("="*80)

    # Process Part1 tables 023-035 (identified as a related sequence)
    table_nums = range(23, 36)  # 023-035 inclusive
    csv_paths = []

    for num in table_nums:
        fpath = data_dir / f"SDS-31_Part1_table_{num:03d}.csv"
        if fpath.exists():
            csv_paths.append(fpath)

    if not csv_paths:
        print("  ⚠ Table sequence not found")
        return

    print(f"\nFound {len(csv_paths)} tables in sequence (Part1 tables 023-035)")
    print(f"  Range: {csv_paths[0].name} to {csv_paths[-1].name}")

    # Process and merge
    merged_df, combined_meta = merge_table_sequence(csv_paths)

    # Save merged result
    output_path = output_dir / "SDS-31_Part1_merged_023-035.csv"
    merged_df.to_csv(output_path, index=False)

    meta_path = output_dir / "SDS-31_Part1_merged_023-035_metadata.json"
    with open(meta_path, 'w') as f:
        json.dump(combined_meta, f, indent=2)

    print(f"\n✓ Merged {len(csv_paths)} tables into single dataset:")
    print(f"  Total rows: {len(merged_df)}")
    print(f"  Columns: {len(merged_df.columns)}")
    print(f"  Saved to: {output_path.name}")

    # Show sample of merged data
    print(f"\n  Sample (first 5 rows of merged data):")
    print(merged_df.head(5).to_string(index=False, max_colwidth=10))

    print(f"\n  Last 5 rows:")
    print(merged_df.tail(5).to_string(index=False, max_colwidth=10))

def main():
    """Main execution"""
    create_database_ready_format()

    # Demonstrate merging a complete table sequence
    demonstrate_table_merging()

    print("\n" + "="*80)
    print("NEXT STEPS FOR FULL DATABASE")
    print("="*80)
    print("""
To create a complete database:

1. Process all 338 tables with this script
2. Merge related table sequences (identified in investigation)
3. Add chemical system identifiers from PDF context
4. Create unified schema:
   - system_id (e.g., "Na3PO4-H2O")
   - temperature_C (extracted from table)
   - component_1_mass_percent
   - component_1_molality
   - component_2_mass_percent
   - component_2_molality
   - phase (A, B, C, etc.)
   - source_pdf (Part1-7)
   - source_table (original table number)
   - reference (if available)

5. Validate:
   - mass% values between 0-100
   - molality > 0
   - phase labels from valid set
   - no duplicate rows

6. Export to:
   - SQLite database
   - JSON for easy parsing
   - Parquet for efficient storage
    """)

if __name__ == "__main__":
    main()
