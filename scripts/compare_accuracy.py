"""
Compare extraction accuracy before and after header improvement.
"""

import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from assess_extraction_accuracy import assess_table_quality


def compare_directories(original_dir: Path, improved_dir: Path, sample_size: int = 100):
    """Compare quality scores between original and improved tables."""

    original_dir = Path(original_dir)
    improved_dir = Path(improved_dir)

    results = {
        'original': {'scores': [], 'avg': {}},
        'improved': {'scores': [], 'avg': {}},
        'improvement': {}
    }

    # Sample tables
    csv_files = sorted(original_dir.glob('*.csv'))[:sample_size]

    print(f"Comparing {len(csv_files)} tables...")

    for csv_file in csv_files:
        try:
            # Original
            df_original = pd.read_csv(csv_file)
            scores_original = assess_table_quality(df_original)
            results['original']['scores'].append(scores_original)

            # Improved
            improved_file = improved_dir / csv_file.name
            if improved_file.exists():
                df_improved = pd.read_csv(improved_file)
                scores_improved = assess_table_quality(df_improved)
                results['improved']['scores'].append(scores_improved)

        except Exception as e:
            continue

    # Calculate averages
    for category in ['original', 'improved']:
        scores = results[category]['scores']
        if scores:
            results[category]['avg'] = {
                'header_quality': sum(s['header_quality'] for s in scores) / len(scores),
                'data_completeness': sum(s['data_completeness'] for s in scores) / len(scores),
                'column_separation': sum(s['column_separation'] for s in scores) / len(scores),
                'numeric_accuracy': sum(s['numeric_accuracy'] for s in scores) / len(scores),
                'overall': sum(s['overall'] for s in scores) / len(scores),
            }

    # Calculate improvements
    for metric in ['header_quality', 'data_completeness', 'column_separation', 'numeric_accuracy', 'overall']:
        original_val = results['original']['avg'].get(metric, 0)
        improved_val = results['improved']['avg'].get(metric, 0)
        results['improvement'][metric] = improved_val - original_val

    return results


def main():
    print("=" * 70)
    print("BEFORE vs AFTER HEADER IMPROVEMENT")
    print("=" * 70)

    original_dir = Path('output/02_cleaned_enhanced')
    improved_dir = Path('output/03_improved_headers')

    results = compare_directories(original_dir, improved_dir, sample_size=100)

    print("\nBEFORE (Original Headers):")
    for metric, score in results['original']['avg'].items():
        print(f"  {metric.replace('_', ' ').title()}: {score:.1f}%")

    print("\nAFTER (Improved Headers):")
    for metric, score in results['improved']['avg'].items():
        print(f"  {metric.replace('_', ' ').title()}: {score:.1f}%")

    print("\nIMPROVEMENT:")
    for metric, improvement in results['improvement'].items():
        direction = "↑" if improvement > 0 else "↓" if improvement < 0 else "="
        print(f"  {metric.replace('_', ' ').title()}: {direction} {abs(improvement):.1f} percentage points")

    overall_before = results['original']['avg']['overall']
    overall_after = results['improved']['avg']['overall']
    improvement_pct = ((overall_after - overall_before) / overall_before) * 100

    print(f"\n{'=' * 70}")
    print(f"OVERALL ACCURACY IMPROVEMENT: {overall_before:.1f}% → {overall_after:.1f}%")
    print(f"Relative improvement: +{improvement_pct:.1f}%")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    main()
