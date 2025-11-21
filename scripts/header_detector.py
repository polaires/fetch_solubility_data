"""
Header Detection and Correction Module

Implements intelligent header detection to fix the #1 extraction issue:
100% of tables have auto-generated numeric headers ("0", "1", "2").

This module provides multiple strategies to detect and assign meaningful headers.
"""

import pandas as pd
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json


class HeaderDetector:
    """Detects and corrects table headers using multiple strategies."""

    def __init__(self):
        self.column_type_keywords = {
            'temperature': ['temp', 'temperature', '°c', '°k', 't', 'celsius', 'kelvin'],
            'mass_percent': ['mass%', 'wt%', 'weight%', 'w', 'mass', 'wt'],
            'molality': ['mol/kg', 'molality', 'm', 'mol kg'],
            'mole_fraction': ['mol%', 'mole%', 'x', 'mole fraction', 'mol frac'],
            'ph': ['ph', 'p.h.'],
            'density': ['density', 'ρ', 'rho', 'g/cm³', 'g/ml'],
            'pressure': ['pressure', 'p', 'bar', 'atm', 'pa', 'mpa'],
            'phase': ['phase', 'solid', 'phases', 'equilibrium'],
            'composition': ['composition', 'comp', 'conc', 'concentration'],
        }

    def detect_headers(
        self,
        df: pd.DataFrame,
        column_types: Optional[Dict] = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Main header detection function that tries multiple strategies.

        Returns:
            - DataFrame with corrected headers
            - Metadata about detection method and confidence
        """
        strategies_tried = []

        # Strategy 1: Check if first row is header row
        result1, confidence1 = self._try_first_row_as_header(df)
        strategies_tried.append({
            'strategy': 'first_row_header',
            'confidence': confidence1,
            'success': confidence1 > 0.7
        })

        if confidence1 > 0.7:
            return result1, {
                'method': 'first_row_header',
                'confidence': confidence1,
                'strategies_tried': strategies_tried
            }

        # Strategy 2: Use column type detection (if available)
        if column_types:
            result2, confidence2 = self._generate_headers_from_types(df, column_types)
            strategies_tried.append({
                'strategy': 'column_type_inference',
                'confidence': confidence2,
                'success': confidence2 > 0.6
            })

            if confidence2 > 0.6:
                return result2, {
                    'method': 'column_type_inference',
                    'confidence': confidence2,
                    'strategies_tried': strategies_tried
                }

        # Strategy 3: Infer from data patterns
        result3, confidence3 = self._infer_headers_from_data(df)
        strategies_tried.append({
            'strategy': 'data_pattern_inference',
            'confidence': confidence3,
            'success': confidence3 > 0.5
        })

        if confidence3 > 0.5:
            return result3, {
                'method': 'data_pattern_inference',
                'confidence': confidence3,
                'strategies_tried': strategies_tried
            }

        # Strategy 4: Generate descriptive numeric headers (fallback)
        result4, confidence4 = self._generate_descriptive_headers(df)
        strategies_tried.append({
            'strategy': 'descriptive_numeric',
            'confidence': confidence4,
            'success': True
        })

        return result4, {
            'method': 'descriptive_numeric',
            'confidence': confidence4,
            'strategies_tried': strategies_tried
        }

    def _try_first_row_as_header(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """
        Check if first row contains header-like text.

        Returns:
            - DataFrame with first row promoted to header (if detected)
            - Confidence score (0.0-1.0)
        """
        if df.empty or len(df) < 2:
            return df, 0.0

        first_row = df.iloc[0]

        # Count how many cells look like headers vs data
        header_score = 0
        total_cells = 0

        for value in first_row:
            if pd.isna(value):
                continue

            total_cells += 1
            value_str = str(value).strip().lower()

            # Header indicators
            is_text = any(c.isalpha() for c in value_str)
            is_short = len(value_str) < 30
            has_keywords = any(
                keyword in value_str
                for keywords in self.column_type_keywords.values()
                for keyword in keywords
            )
            is_not_pure_number = not re.match(r'^-?\d+\.?\d*$', value_str)

            if is_text and is_short and is_not_pure_number:
                header_score += 1
            if has_keywords:
                header_score += 0.5  # Bonus for containing keywords

        if total_cells == 0:
            return df, 0.0

        confidence = min(header_score / total_cells, 1.0)

        if confidence > 0.7:
            # Promote first row to header
            new_df = df.iloc[1:].copy()
            new_df.columns = first_row.values
            return new_df, confidence

        return df, confidence

    def _generate_headers_from_types(
        self,
        df: pd.DataFrame,
        column_types: Dict
    ) -> Tuple[pd.DataFrame, float]:
        """
        Generate headers based on detected column types.

        Args:
            column_types: Dict from column_standardizer.py with detected types

        Returns:
            - DataFrame with new headers
            - Confidence score based on type detection confidence
        """
        new_headers = []
        total_confidence = 0
        count = 0

        for col_idx, col in enumerate(df.columns):
            col_str = str(col)

            if col_str in column_types:
                type_info = column_types[col_str]
                detected_type = type_info.get('detected_type', 'unknown')
                confidence = type_info.get('confidence', 0.5)

                # Generate readable header from type
                header = self._type_to_header(detected_type, col_idx)
                new_headers.append(header)

                total_confidence += confidence
                count += 1
            else:
                new_headers.append(f"Column_{col_idx}")
                total_confidence += 0.3
                count += 1

        avg_confidence = total_confidence / count if count > 0 else 0

        new_df = df.copy()
        new_df.columns = new_headers

        return new_df, avg_confidence

    def _type_to_header(self, column_type: str, index: int) -> str:
        """Convert column type to readable header."""
        type_map = {
            'temperature': 'Temperature',
            'mass_percent': 'Mass %',
            'molality': 'Molality (mol/kg)',
            'mole_fraction': 'Mole Fraction',
            'ph': 'pH',
            'density': 'Density (g/cm³)',
            'pressure': 'Pressure',
            'phase': 'Phase',
            'composition': 'Composition',
            'numeric': f'Data_{index}',
            'text': f'Text_{index}',
        }
        return type_map.get(column_type, f'Column_{index}')

    def _infer_headers_from_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """
        Infer column types by analyzing data patterns in each column.

        Returns:
            - DataFrame with inferred headers
            - Confidence score
        """
        new_headers = []
        confidences = []

        for col in df.columns:
            # Sample first 20 non-null values
            sample = df[col].dropna().head(20)

            if len(sample) == 0:
                new_headers.append(f"Empty_{col}")
                confidences.append(0.1)
                continue

            # Analyze patterns
            header, confidence = self._infer_single_column_type(sample)
            new_headers.append(header)
            confidences.append(confidence)

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        new_df = df.copy()
        new_df.columns = new_headers

        return new_df, avg_confidence

    def _infer_single_column_type(self, sample: pd.Series) -> Tuple[str, float]:
        """Infer type of a single column from sample data."""
        sample_str = ' '.join(str(v).lower() for v in sample)

        # Temperature detection (values 0-500, units)
        if re.search(r'\d+\.?\d*\s*°', sample_str) or \
           all(self._is_temperature_range(v) for v in sample if pd.notna(v)):
            return 'Temperature (°C)', 0.8

        # Mass percent (0-100 range or % symbol)
        if '%' in sample_str or \
           all(self._is_percentage_range(v) for v in sample if pd.notna(v)):
            return 'Mass %', 0.75

        # pH (0-14 range)
        if all(self._is_ph_range(v) for v in sample if pd.notna(v)):
            return 'pH', 0.7

        # Phase labels (A, B, II, III, etc.)
        if all(self._is_phase_label(v) for v in sample if pd.notna(v)):
            return 'Phase', 0.85

        # Molality/mole fraction (small decimals)
        if all(self._is_small_decimal(v) for v in sample if pd.notna(v)):
            return 'Molality', 0.6

        # Generic numeric
        if all(self._is_numeric(v) for v in sample if pd.notna(v)):
            return 'Numeric Data', 0.5

        # Text
        return 'Text Data', 0.4

    def _generate_descriptive_headers(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """
        Generate descriptive headers as last resort.
        Better than "0", "1", "2" but not semantic.
        """
        new_headers = []

        for idx, col in enumerate(df.columns):
            # Check if current header is just a number
            if str(col).isdigit() or 'Unnamed' in str(col):
                new_headers.append(f"Column_{chr(65 + idx)}")  # Column_A, Column_B, etc.
            else:
                new_headers.append(str(col))

        new_df = df.copy()
        new_df.columns = new_headers

        return new_df, 0.3  # Low confidence, but better than nothing

    # Helper methods for type checking

    def _is_temperature_range(self, value) -> bool:
        """Check if value looks like temperature (typically -50 to 500°C)."""
        try:
            num = float(str(value).replace('°C', '').replace('°', '').strip())
            return -100 <= num <= 500
        except:
            return False

    def _is_percentage_range(self, value) -> bool:
        """Check if value is in 0-100 range (mass %)."""
        try:
            num = float(str(value).replace('%', '').strip())
            return 0 <= num <= 100
        except:
            return False

    def _is_ph_range(self, value) -> bool:
        """Check if value is in pH range (0-14)."""
        try:
            num = float(str(value).strip())
            return 0 <= num <= 14
        except:
            return False

    def _is_phase_label(self, value) -> bool:
        """Check if value looks like phase label (A, B, II, etc.)."""
        value_str = str(value).strip()
        return bool(re.match(r'^([A-F]|I{1,4}|IV|V|VI)(\+[A-F])?$', value_str))

    def _is_small_decimal(self, value) -> bool:
        """Check if value is small decimal (< 10, typical for molality)."""
        try:
            num = float(str(value).strip())
            return 0 <= num < 10
        except:
            return False

    def _is_numeric(self, value) -> bool:
        """Check if value is numeric."""
        try:
            float(str(value).strip())
            return True
        except:
            return False


def improve_headers_batch(
    input_dir: Path,
    output_dir: Path,
    metadata_dir: Path,
    use_column_types: bool = True
):
    """
    Apply header detection to all tables in a directory.

    Args:
        input_dir: Directory with CSV files (original headers)
        output_dir: Directory to save improved CSV files
        metadata_dir: Directory with column type metadata (optional)
        use_column_types: Whether to use column type detection
    """
    detector = HeaderDetector()

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    metadata_dir = Path(metadata_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        'total_files': 0,
        'improved': 0,
        'methods_used': {},
        'avg_confidence': 0.0,
        'files': []
    }

    csv_files = sorted(input_dir.glob('*.csv'))
    total_confidence = 0

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            original_headers = list(df.columns)

            # Load column types if available
            column_types = None
            if use_column_types and metadata_dir.exists():
                metadata_file = metadata_dir / f"{csv_file.stem}_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                        column_types = metadata.get('column_analysis', {}).get('types_detected', {})

            # Detect headers
            improved_df, detection_info = detector.detect_headers(df, column_types)
            new_headers = list(improved_df.columns)

            # Check if headers actually improved
            improved = new_headers != original_headers

            # Save improved table
            output_file = output_dir / csv_file.name
            improved_df.to_csv(output_file, index=False)

            # Track results
            method = detection_info['method']
            confidence = detection_info['confidence']

            results['total_files'] += 1
            if improved:
                results['improved'] += 1
            results['methods_used'][method] = results['methods_used'].get(method, 0) + 1
            total_confidence += confidence

            results['files'].append({
                'filename': csv_file.name,
                'original_headers': [str(h) for h in original_headers[:5]],  # First 5, convert to str
                'new_headers': [str(h) for h in new_headers[:5]],  # First 5, convert to str
                'method': method,
                'confidence': float(confidence),
                'improved': bool(improved)
            })

            if results['total_files'] % 50 == 0:
                print(f"Processed {results['total_files']} files...")

        except Exception as e:
            print(f"Error processing {csv_file.name}: {e}")
            continue

    results['avg_confidence'] = float(total_confidence / results['total_files']) if results['total_files'] > 0 else 0.0

    # Save summary report
    report_file = output_dir / '_header_improvement_report.json'
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)

    return results


def main():
    """Test header detection on sample tables."""
    print("=" * 70)
    print("HEADER DETECTION TEST")
    print("=" * 70)

    # Test on existing enhanced data
    input_dir = Path('output/02_cleaned_enhanced')
    output_dir = Path('output/03_improved_headers')
    metadata_dir = Path('output/02_cleaned_enhanced')

    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return

    print(f"\nProcessing tables from: {input_dir}")
    print(f"Saving improved tables to: {output_dir}")
    print(f"Using metadata from: {metadata_dir}")

    results = improve_headers_batch(
        input_dir=input_dir,
        output_dir=output_dir,
        metadata_dir=metadata_dir,
        use_column_types=True
    )

    print(f"\n{'=' * 70}")
    print("RESULTS")
    print(f"{'=' * 70}")
    print(f"Total files processed: {results['total_files']}")
    print(f"Headers improved: {results['improved']} ({results['improved']/results['total_files']*100:.1f}%)")
    print(f"Average confidence: {results['avg_confidence']:.2f}")

    print(f"\nMethods used:")
    for method, count in results['methods_used'].items():
        pct = count / results['total_files'] * 100
        print(f"  {method}: {count} tables ({pct:.1f}%)")

    # Show sample improvements
    print(f"\nSample improvements (first 5 files):")
    for file_info in results['files'][:5]:
        print(f"\n{file_info['filename']}:")
        print(f"  Method: {file_info['method']} (confidence: {file_info['confidence']:.2f})")
        print(f"  Original: {file_info['original_headers']}")
        print(f"  Improved: {file_info['new_headers']}")

    print(f"\n✓ Full report saved to: {output_dir}/_header_improvement_report.json")


if __name__ == '__main__':
    main()
