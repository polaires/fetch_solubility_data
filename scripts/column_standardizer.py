"""
Column Standardization Module

Detects and standardizes column types in solubility data tables.
Identifies columns for: mass%, molality, temperature, pH, phase, etc.
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Optional


class ColumnStandardizer:
    """Standardizes column names and types across tables"""

    # Standard column name mappings
    STANDARD_NAMES = {
        'temperature': ['temp', 't', '°c', 'celsius', 'kelvin', 'k'],
        'mass_percent': ['mass%', 'wt%', 'weight%', 'mass percent', 'wt percent'],
        'molality': ['mol/kg', 'molality', 'm', 'molal'],
        'mole_fraction': ['mol%', 'mole%', 'x', 'mole fraction'],
        'ph': ['ph', 'p.h.'],
        'phase': ['phase', 'solid', 'solid phase'],
        'density': ['density', 'ρ', 'rho', 'g/cm3'],
        'composition': ['composition', 'comp'],
    }

    def __init__(self):
        self.column_mapping = {}
        self.column_types = {}

    def detect_column_type(self, header: str, sample_values: List) -> Tuple[str, float]:
        """
        Detect the type of a column based on header and sample values.

        Args:
            header: Column header string
            sample_values: List of sample values from the column

        Returns:
            Tuple of (column_type, confidence_score)
        """
        header_lower = str(header).lower().strip()
        sample_str = ' '.join(str(v) for v in sample_values if pd.notna(v)).lower()

        # Temperature detection
        if any(t in header_lower for t in ['temp', '°c', '°k', 'celsius', 'kelvin']):
            return 'temperature', 0.95
        if re.search(r'\d+\.?\d*\s*°', sample_str):
            return 'temperature', 0.85

        # Mass percent detection
        if 'mass%' in header_lower or 'wt%' in header_lower:
            return 'mass_percent', 0.95
        if re.search(r'\d+\.?\d*\s*%', sample_str):
            return 'mass_percent', 0.80

        # Molality detection
        if 'mol/kg' in header_lower or 'molality' in header_lower:
            return 'molality', 0.95

        # Mole fraction detection
        if 'mol%' in header_lower or 'mole%' in header_lower:
            return 'mole_fraction', 0.90

        # pH detection
        if header_lower == 'ph' or 'p.h.' in header_lower:
            return 'ph', 0.95
        # pH values typically 0-14
        if self._check_ph_range(sample_values):
            return 'ph', 0.70

        # Phase detection
        if 'phase' in header_lower or 'solid' in header_lower:
            return 'phase', 0.95
        # Check for phase labels (A, B, C, II, III, etc.)
        if self._check_phase_labels(sample_values):
            return 'phase', 0.85

        # Density detection
        if 'density' in header_lower or header_lower in ['ρ', 'rho']:
            return 'density', 0.95

        # Numeric data (generic)
        if self._is_numeric_column(sample_values):
            return 'numeric', 0.60

        # Text/label column
        return 'text', 0.50

    def _check_ph_range(self, values: List) -> bool:
        """Check if values fall in typical pH range (0-14)"""
        numeric_vals = []
        for v in values:
            if pd.isna(v):
                continue
            try:
                num = float(str(v).replace(',', '.').strip())
                numeric_vals.append(num)
            except:
                continue

        if len(numeric_vals) < 3:
            return False

        # Check if most values are in pH range
        in_range = sum(1 for v in numeric_vals if 0 <= v <= 14)
        return in_range / len(numeric_vals) > 0.8

    def _check_phase_labels(self, values: List) -> bool:
        """Check if values look like phase labels"""
        phase_pattern = r'^[A-F]$|^I{1,3}$|^[A-F]\+[A-F]$|^[A-F]0\.\d+$'

        matches = 0
        total = 0

        for v in values:
            if pd.isna(v) or str(v).strip() == '':
                continue
            total += 1
            if re.match(phase_pattern, str(v).strip()):
                matches += 1

        if total == 0:
            return False

        return matches / total > 0.5

    def _is_numeric_column(self, values: List) -> bool:
        """Check if column contains mostly numeric values"""
        numeric_count = 0
        total = 0

        for v in values:
            if pd.isna(v) or str(v).strip() in ['', '----', '---']:
                continue
            total += 1

            # Try to parse as number
            try:
                cleaned = str(v).replace(',', '.').replace(' ', '').strip()
                # Remove phase markers in parentheses
                cleaned = re.sub(r'\([A-F+]\)', '', cleaned).strip()
                float(cleaned)
                numeric_count += 1
            except:
                pass

        if total == 0:
            return False

        return numeric_count / total > 0.7

    def standardize_column_name(self, original_name: str, detected_type: str) -> str:
        """
        Create a standardized column name.

        Args:
            original_name: Original column header
            detected_type: Detected column type

        Returns:
            Standardized column name
        """
        # If it's a generic numeric column, try to keep meaningful name
        if detected_type == 'numeric':
            cleaned = str(original_name).strip()
            if cleaned and cleaned != 'Unnamed' and not cleaned.isdigit():
                return cleaned.replace(' ', '_').lower()
            return f"col_{original_name}"

        # For typed columns, use standard names
        type_names = {
            'temperature': 'temperature_C',
            'mass_percent': 'mass_percent',
            'molality': 'molality_mol_kg',
            'mole_fraction': 'mole_fraction',
            'ph': 'pH',
            'phase': 'phase',
            'density': 'density_g_cm3',
            'text': 'label',
        }

        base_name = type_names.get(detected_type, detected_type)

        # Add counter if we've seen this type before
        counter = 1
        std_name = base_name
        while std_name in self.column_mapping.values():
            counter += 1
            std_name = f"{base_name}_{counter}"

        return std_name

    def analyze_table(self, df: pd.DataFrame, sample_size: int = 20) -> Dict:
        """
        Analyze a table and detect column types.

        Args:
            df: DataFrame to analyze
            sample_size: Number of rows to sample for detection

        Returns:
            Dict with column analysis results
        """
        results = {
            'columns': {},
            'summary': {
                'temperature_cols': 0,
                'composition_cols': 0,
                'phase_cols': 0,
                'numeric_cols': 0,
                'text_cols': 0,
            }
        }

        for col in df.columns:
            # Get sample values (skip nulls)
            sample = df[col].dropna().head(sample_size).tolist()

            # Detect type
            col_type, confidence = self.detect_column_type(col, sample)

            # Generate standard name
            std_name = self.standardize_column_name(col, col_type)

            results['columns'][col] = {
                'original_name': col,
                'standard_name': std_name,
                'detected_type': col_type,
                'confidence': confidence,
                'sample_values': sample[:5],  # Store first 5 for inspection
            }

            # Update summary counts
            if col_type == 'temperature':
                results['summary']['temperature_cols'] += 1
            elif col_type in ['mass_percent', 'molality', 'mole_fraction']:
                results['summary']['composition_cols'] += 1
            elif col_type == 'phase':
                results['summary']['phase_cols'] += 1
            elif col_type == 'numeric':
                results['summary']['numeric_cols'] += 1
            else:
                results['summary']['text_cols'] += 1

        return results

    def apply_standardization(self, df: pd.DataFrame, analysis: Dict) -> pd.DataFrame:
        """
        Apply column standardization to a DataFrame.

        Args:
            df: Original DataFrame
            analysis: Analysis results from analyze_table()

        Returns:
            DataFrame with standardized column names
        """
        rename_mapping = {
            col: info['standard_name']
            for col, info in analysis['columns'].items()
        }

        df_std = df.rename(columns=rename_mapping)

        return df_std

    def create_column_metadata(self, analysis: Dict) -> Dict:
        """
        Create metadata about columns for API/UI consumption.

        Args:
            analysis: Analysis results

        Returns:
            Metadata dict with column info
        """
        metadata = {
            'column_types': {},
            'display_info': {},
        }

        for col, info in analysis['columns'].items():
            std_name = info['standard_name']
            col_type = info['detected_type']

            metadata['column_types'][std_name] = col_type

            # Add display formatting info
            display = {
                'label': std_name.replace('_', ' ').title(),
                'type': col_type,
            }

            # Add units/formatting hints
            if col_type == 'temperature':
                display['unit'] = '°C'
                display['format'] = '.1f'
            elif col_type == 'mass_percent':
                display['unit'] = '%'
                display['format'] = '.2f'
            elif col_type == 'molality':
                display['unit'] = 'mol/kg'
                display['format'] = '.4f'
            elif col_type == 'mole_fraction':
                display['format'] = '.4f'
            elif col_type == 'ph':
                display['format'] = '.2f'
            elif col_type == 'density':
                display['unit'] = 'g/cm³'
                display['format'] = '.3f'

            metadata['display_info'][std_name] = display

        return metadata


def standardize_table_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Convenience function to standardize a table's columns.

    Args:
        df: Input DataFrame

    Returns:
        Tuple of (standardized DataFrame, metadata dict)
    """
    standardizer = ColumnStandardizer()
    analysis = standardizer.analyze_table(df)
    df_std = standardizer.apply_standardization(df, analysis)
    metadata = standardizer.create_column_metadata(analysis)

    return df_std, metadata
