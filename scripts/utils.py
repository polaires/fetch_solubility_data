"""
Shared utility functions for solubility data processing pipeline
"""

import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def advanced_clean(value) -> Optional[str]:
    """
    Advanced cleaning for OCR artifacts in extracted data

    Args:
        value: Raw value from extracted table

    Returns:
        Cleaned string value or None if empty
    """
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


def extract_phase_marker(value) -> Optional[str]:
    """
    Extract phase label from value like '0.026 (D)'

    Args:
        value: Value potentially containing phase marker

    Returns:
        Phase label (e.g., "D") or None
    """
    if pd.isna(value):
        return None

    text = str(value)
    match = re.search(r'[\(\[]([A-Z][\w.]*?)[\)\]]', text)
    if match:
        return match.group(1)
    return None


def identify_column_type(col_name: str) -> str:
    """
    Identify data type from column name

    Args:
        col_name: Column name/header text

    Returns:
        Column type identifier
    """
    col_lower = col_name.lower()

    if 'mass%' in col_lower or 'mass  %' in col_lower:
        return 'mass_percent'
    elif 'mol%' in col_lower or 'mol  %' in col_lower:
        return 'mol_percent'
    elif 'mol/kg' in col_lower or 'molkg' in col_lower:
        return 'molality'
    elif 'phase' in col_lower:
        return 'phase'
    elif 'temp' in col_lower:
        return 'temperature'
    else:
        return 'unknown'


def parse_pdf_filename(pdf_path: Path) -> Dict[str, str]:
    """
    Parse PDF filename to extract metadata

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dict with series, part, etc.
    """
    stem = pdf_path.stem

    # Try to match SDS-31_PartN pattern
    match = re.match(r'(SDS-\d+)_Part(\d+)', stem)
    if match:
        return {
            'series': match.group(1),
            'part': f"Part{match.group(2)}",
            'part_num': int(match.group(2)),
            'filename': pdf_path.name,
            'stem': stem
        }

    # Generic fallback
    return {
        'series': 'Unknown',
        'part': stem,
        'part_num': 0,
        'filename': pdf_path.name,
        'stem': stem
    }


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists, create if needed

    Args:
        path: Directory path

    Returns:
        Path object (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def count_numeric_values(df: pd.DataFrame) -> int:
    """
    Count numeric values in dataframe

    Args:
        df: DataFrame to analyze

    Returns:
        Count of cells containing numeric data
    """
    count = 0
    for val in df.values.flatten():
        if pd.notna(val) and re.search(r'\d+\.?\d*', str(val)):
            count += 1
    return count


def has_data_type(df: pd.DataFrame, data_type: str) -> bool:
    """
    Check if dataframe contains specific data type

    Args:
        df: DataFrame to check
        data_type: Type to look for (e.g., "mass%", "mol/kg", "phase")

    Returns:
        True if data type is present
    """
    # Check in first few rows (likely headers)
    text = ' '.join([str(val) for val in df.iloc[:3].values.flatten() if pd.notna(val)]).lower()

    if data_type == "mass%":
        return 'mass%' in text or 'mass  %' in text
    elif data_type == "mol%":
        return 'mol%' in text or 'mol  %' in text
    elif data_type == "molality":
        return 'mol/kg' in text or 'molkg' in text
    elif data_type == "phase":
        return 'phase' in text or any(p in text for p in [' a ', ' b ', ' c ', ' ii ', ' iii '])
    elif data_type == "temperature":
        return any(t in text for t in ['temp', '°c', '°k', 'k.'])

    return False


def format_table_summary(table_info: Dict) -> str:
    """
    Format table information as readable summary

    Args:
        table_info: Dict with table metadata

    Returns:
        Formatted summary string
    """
    lines = [
        f"File: {table_info.get('file', 'unknown')}",
        f"  Size: {table_info.get('rows', 0)} rows × {table_info.get('cols', 0)} columns",
    ]

    if 'numeric_count' in table_info:
        lines.append(f"  Numeric values: {table_info['numeric_count']}")

    data_types = []
    for key, val in table_info.items():
        if key.startswith('has_') and val:
            data_types.append(key.replace('has_', ''))

    if data_types:
        lines.append(f"  Data types: {', '.join(data_types)}")

    return '\n'.join(lines)


def make_columns_unique(columns: List[str]) -> List[str]:
    """
    Make column names unique by adding numeric suffixes

    Args:
        columns: List of column names (may have duplicates)

    Returns:
        List of unique column names
    """
    new_cols = []
    col_counts = {}

    for col in columns:
        if col in col_counts:
            col_counts[col] += 1
            new_cols.append(f"{col}_{col_counts[col]}")
        else:
            col_counts[col] = 0
            new_cols.append(col)

    return new_cols


# Constants for validation
VALID_PHASES = [
    'A', 'B', 'C', 'D', 'E', 'F',
    'II', 'III', 'IV',
    'D0.5',
    'A+B', 'B+C', 'C+D', 'D+E',
    'A+II', 'B+II', 'C+II',
]

# OCR artifact patterns
OCR_FIXES = [
    ('mo1', 'mol'),
    ('Q .', '0.'),
    ('a .', '0.'),
    ('I I', 'II'),
    ('0. so', '0.50'),
    ('. so', '.50'),
]
