"""
Phase Marker Extraction Module

Extracts phase labels from data values and separates them into dedicated columns.
Handles patterns like: "0.026 (D)", "1.35 (A+B)", "7.5 II", etc.
"""

import pandas as pd
import re
from typing import Tuple, Optional, Dict


class PhaseExtractor:
    """Extracts phase markers from numeric values"""

    # Phase label patterns
    PHASE_PATTERNS = [
        # Parenthetical phases: (A), (B), (A+B), (D0.5)
        r'\s*\(([A-F](?:\+[A-F])?|[A-F]\d+\.?\d*)\)\s*$',
        # Spaced phases: A, B, II, III
        r'\s+([A-F]|I{1,3}|IV|V|VI)\s*$',
        # Combined: A+B, B+C
        r'\s+([A-F]\+[A-F])\s*$',
    ]

    def __init__(self):
        self.combined_pattern = '|'.join(f'({p})' for p in self.PHASE_PATTERNS)

    def extract_phase(self, value: any) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract phase marker from a value.

        Args:
            value: Value that may contain phase marker

        Returns:
            Tuple of (cleaned_value, phase_marker)
            If no phase found, returns (original_value, None)
        """
        if pd.isna(value):
            return None, None

        value_str = str(value).strip()

        # Quick check: if it's purely alphabetic and short, it might be just a phase label
        if len(value_str) <= 5 and re.match(r'^[A-F](\+[A-F])?$|^I{1,3}$', value_str):
            return None, value_str

        # Try to find phase pattern
        for pattern in self.PHASE_PATTERNS:
            match = re.search(pattern, value_str)
            if match:
                # Extract phase label (first captured group that's not None)
                phase = next((g for g in match.groups() if g is not None), None)

                # Remove phase from value
                cleaned = re.sub(pattern, '', value_str).strip()

                # If cleaned value is empty or just punctuation, return None for value
                if not cleaned or cleaned in ['', '-', '--', '----', '---']:
                    return None, phase

                return cleaned, phase

        # No phase found
        return value_str if value_str not in ['', '-', '--', '----'] else None, None

    def extract_from_series(self, series: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """
        Extract phases from an entire pandas Series.

        Args:
            series: Pandas Series with potential phase markers

        Returns:
            Tuple of (cleaned_values_series, phase_series)
        """
        results = series.apply(self.extract_phase)

        # Unpack tuples into two series
        values = results.apply(lambda x: x[0])
        phases = results.apply(lambda x: x[1])

        return values, phases

    def process_dataframe(self, df: pd.DataFrame, numeric_only: bool = True) -> pd.DataFrame:
        """
        Process entire DataFrame to extract phase markers.

        Args:
            df: Input DataFrame
            numeric_only: If True, only process columns that look numeric

        Returns:
            DataFrame with phase columns added
        """
        df_processed = df.copy()
        phase_columns = {}

        for col in df.columns:
            # Skip if explicitly a phase column already
            if 'phase' in str(col).lower():
                continue

            # Check if column should be processed
            if numeric_only:
                # Sample first few non-null values
                sample = df[col].dropna().head(10)
                if len(sample) == 0:
                    continue

                # Check if any values contain phase markers
                has_phase = any(
                    re.search(self.combined_pattern, str(v))
                    for v in sample
                )

                if not has_phase:
                    continue

            # Extract phases
            cleaned_values, phases = self.extract_from_series(df[col])

            # Update the column with cleaned values
            df_processed[col] = cleaned_values

            # If we found any phases, add a phase column
            if phases.notna().any():
                phase_col_name = f"{col}_phase"
                df_processed[phase_col_name] = phases
                phase_columns[col] = phase_col_name

        return df_processed

    def get_unique_phases(self, df: pd.DataFrame) -> set:
        """
        Get all unique phase labels in a DataFrame.

        Args:
            df: DataFrame to analyze

        Returns:
            Set of unique phase labels
        """
        phases = set()

        for col in df.columns:
            if 'phase' in str(col).lower():
                unique = df[col].dropna().unique()
                phases.update(unique)

        return phases


def extract_phases_from_table(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Convenience function to extract phases from a table.

    Args:
        df: Input DataFrame

    Returns:
        Tuple of (processed DataFrame, metadata dict)
    """
    extractor = PhaseExtractor()
    df_processed = extractor.process_dataframe(df)

    unique_phases = extractor.get_unique_phases(df_processed)

    metadata = {
        'phases_found': list(unique_phases),
        'phase_columns_added': sum(1 for col in df_processed.columns if '_phase' in col),
        'total_phase_values': sum(
            df_processed[col].notna().sum()
            for col in df_processed.columns
            if '_phase' in col
        )
    }

    return df_processed, metadata


# Example usage and testing
if __name__ == '__main__':
    # Test with sample data
    test_data = {
        'col1': ['0.026 (D)', '1.35 (A+B)', '7.5', '0.042 (C)', None],
        'col2': ['25.0', '30.0 II', '35.0', '40.0 III', '45.0'],
        'col3': ['A', 'B', 'A+B', 'C', 'D'],
    }

    df = pd.DataFrame(test_data)
    print("Original DataFrame:")
    print(df)
    print()

    df_processed, metadata = extract_phases_from_table(df)
    print("Processed DataFrame:")
    print(df_processed)
    print()
    print("Metadata:")
    print(metadata)
