"""
Extraction Accuracy Assessment and Improvement Recommendations

This script evaluates current extraction accuracy and tests improved methods.
"""

import pandas as pd
import tabula
from pathlib import Path
from typing import Dict, List, Tuple
import json


def assess_table_quality(df: pd.DataFrame) -> Dict:
    """
    Assess quality metrics for an extracted table.

    Returns dict with quality scores (0-100).
    """
    scores = {
        'header_quality': 0,
        'data_completeness': 0,
        'column_separation': 0,
        'numeric_accuracy': 0,
        'overall': 0
    }

    if df.empty:
        return scores

    # 1. Header quality (proper names vs "Unnamed: 0", "0", "1")
    unnamed_cols = sum(1 for col in df.columns if 'Unnamed' in str(col) or str(col).isdigit())
    scores['header_quality'] = max(0, 100 - (unnamed_cols / len(df.columns) * 100))

    # 2. Data completeness (non-null ratio)
    non_null_ratio = df.notna().sum().sum() / (df.shape[0] * df.shape[1])
    scores['data_completeness'] = non_null_ratio * 100

    # 3. Column separation (check for merged columns)
    # Count cells with too many values
    merged_count = 0
    for col in df.columns:
        sample = df[col].astype(str).head(10)
        merged_count += sum(1 for v in sample if len(v.split()) > 6)
    scores['column_separation'] = max(0, 100 - (merged_count / len(df.columns) * 20))

    # 4. Numeric accuracy (cells that look numeric)
    numeric_cells = 0
    total_cells = 0
    for col in df.columns:
        for val in df[col].dropna():
            total_cells += 1
            # Try to parse as number
            cleaned = str(val).replace(',', '.').replace(' ', '').strip()
            try:
                float(cleaned)
                numeric_cells += 1
            except:
                # Check if it's text (not a parsing error)
                if len(cleaned) < 3 or any(c.isalpha() for c in cleaned):
                    numeric_cells += 0.5  # Partial credit for valid text

    if total_cells > 0:
        scores['numeric_accuracy'] = (numeric_cells / total_cells) * 100

    # Overall score
    scores['overall'] = sum(scores.values()) / 4

    return scores


def test_extraction_method(
    pdf_path: Path,
    page: int,
    method: str,
    **kwargs
) -> Tuple[pd.DataFrame, float]:
    """
    Test an extraction method and return the best table + time taken.
    """
    import time

    start = time.time()

    try:
        if method == 'default':
            tables = tabula.read_pdf(str(pdf_path), pages=str(page), multiple_tables=True, **kwargs)
        elif method == 'lattice':
            tables = tabula.read_pdf(str(pdf_path), pages=str(page), multiple_tables=True, lattice=True, **kwargs)
        elif method == 'stream':
            tables = tabula.read_pdf(str(pdf_path), pages=str(page), multiple_tables=True, stream=True, **kwargs)
        elif method == 'guess':
            tables = tabula.read_pdf(str(pdf_path), pages=str(page), multiple_tables=True, guess=True, **kwargs)
        elif method == 'area':
            # Manual area specification (most accurate but requires configuration)
            tables = tabula.read_pdf(str(pdf_path), pages=str(page), area=kwargs.get('area'), **kwargs)
        else:
            return None, 0

        elapsed = time.time() - start

        if tables and len(tables) > 0:
            return tables[0], elapsed
        return None, elapsed

    except Exception as e:
        return None, time.time() - start


def compare_extraction_methods(pdf_path: Path, test_pages: List[int] = [10, 15, 20]) -> Dict:
    """
    Compare different extraction methods across multiple pages.
    """
    methods = ['default', 'stream', 'guess']
    results = {}

    for page in test_pages:
        page_results = {}

        for method in methods:
            df, time_taken = test_extraction_method(pdf_path, page, method)

            if df is not None:
                quality = assess_table_quality(df)
                page_results[method] = {
                    'shape': df.shape,
                    'quality_scores': quality,
                    'time_ms': int(time_taken * 1000)
                }
            else:
                page_results[method] = {
                    'shape': (0, 0),
                    'quality_scores': {'overall': 0},
                    'time_ms': 0
                }

        results[f'page_{page}'] = page_results

    return results


def analyze_current_accuracy() -> Dict:
    """
    Analyze accuracy of current extraction.
    """
    data_dir = Path('web-interface/public/data')

    all_scores = []
    issues = {
        'header_problems': 0,
        'high_null_rate': 0,
        'merged_columns': 0,
        'low_overall': 0
    }

    for csv_file in sorted(data_dir.glob('*.csv'))[:100]:  # Sample 100 tables
        try:
            df = pd.read_csv(csv_file)
            scores = assess_table_quality(df)
            all_scores.append(scores)

            # Track issues
            if scores['header_quality'] < 20:
                issues['header_problems'] += 1
            if scores['data_completeness'] < 70:
                issues['high_null_rate'] += 1
            if scores['column_separation'] < 80:
                issues['merged_columns'] += 1
            if scores['overall'] < 60:
                issues['low_overall'] += 1

        except Exception as e:
            continue

    # Calculate averages
    avg_scores = {
        'header_quality': sum(s['header_quality'] for s in all_scores) / len(all_scores),
        'data_completeness': sum(s['data_completeness'] for s in all_scores) / len(all_scores),
        'column_separation': sum(s['column_separation'] for s in all_scores) / len(all_scores),
        'numeric_accuracy': sum(s['numeric_accuracy'] for s in all_scores) / len(all_scores),
        'overall': sum(s['overall'] for s in all_scores) / len(all_scores),
    }

    return {
        'tables_analyzed': len(all_scores),
        'average_scores': avg_scores,
        'issues': issues,
        'estimated_accuracy': avg_scores['overall']
    }


def main():
    """Run accuracy assessment."""
    print("="*70)
    print("EXTRACTION ACCURACY ASSESSMENT")
    print("="*70)

    # Assess current extraction
    print("\n1. Analyzing current extraction quality...")
    current = analyze_current_accuracy()

    print(f"\nTables analyzed: {current['tables_analyzed']}")
    print(f"\nAverage Quality Scores:")
    for metric, score in current['average_scores'].items():
        print(f"  {metric.replace('_', ' ').title()}: {score:.1f}%")

    print(f"\n**ESTIMATED OVERALL ACCURACY: {current['estimated_accuracy']:.1f}%**")

    print(f"\nCommon Issues:")
    for issue, count in current['issues'].items():
        pct = count / current['tables_analyzed'] * 100
        print(f"  {issue.replace('_', ' ').title()}: {count} tables ({pct:.1f}%)")

    # Test alternative methods
    print("\n\n2. Testing alternative extraction methods...")
    pdf_path = Path('Data/SDS-31_Part3.pdf')
    if pdf_path.exists():
        comparison = compare_extraction_methods(pdf_path, [10, 15, 20])

        print("\nMethod Comparison (average across 3 pages):")
        method_avgs = {}
        for method in ['default', 'stream', 'guess']:
            scores = [comparison[page][method]['quality_scores']['overall']
                     for page in comparison if method in comparison[page]]
            if scores:
                method_avgs[method] = sum(scores) / len(scores)
                print(f"  {method.upper()}: {method_avgs[method]:.1f}% quality")

        best_method = max(method_avgs.items(), key=lambda x: x[1])
        print(f"\n  → Best method: {best_method[0].upper()} ({best_method[1]:.1f}%)")

    # Save results
    output = {
        'current_accuracy': current,
        'timestamp': pd.Timestamp.now().isoformat()
    }

    output_file = Path('output/extraction_accuracy_report.json')
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n\n✓ Full report saved to: {output_file}")


if __name__ == '__main__':
    main()
