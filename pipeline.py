#!/usr/bin/env python3
"""
Automated Pipeline for Solubility Data Processing

This is the main entry point for processing PDF booklets containing
solubility data. It orchestrates the entire workflow from extraction
to database-ready output.

Usage:
    # Process all PDFs in Data/ directory
    python pipeline.py --all

    # Process specific PDF
    python pipeline.py --pdf Data/SDS-31_Part1.pdf

    # Resume from specific stage
    python pipeline.py --all --start-from clean

    # Process with custom config
    python pipeline.py --all --config my_config.yaml
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import yaml
import json

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from scripts import extract, clean
# prepare_db and analyze will be imported when we create them


class Pipeline:
    """Main pipeline orchestrator"""

    def __init__(self, config_path: Path = None):
        """Initialize pipeline with configuration"""
        self.config = self.load_config(config_path)
        self.results = {}
        self.start_time = datetime.now()

    def load_config(self, config_path: Path = None) -> dict:
        """Load configuration from YAML file"""
        if config_path and config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)

        # Default configuration
        return {
            'directories': {
                'input': 'Data',
                'output_base': 'output',
                'extracted': 'output/01_extracted',
                'cleaned': 'output/02_cleaned',
                'analyzed': 'output/03_analyzed',
                'database': 'output/04_database',
            },
            'extraction': {
                'pages': 'all',
                'multiple_tables': True,
            },
            'cleaning': {
                'apply_ocr_fixes': True,
            },
            'database': {
                'merge_sequences': True,
                'export_formats': ['csv', 'json'],
            }
        }

    def run_stage(self, stage_name: str, stage_func, *args, **kwargs):
        """Run a pipeline stage with error handling"""
        print("\n" + "="*80)
        print(f"STAGE: {stage_name.upper()}")
        print("="*80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        try:
            result = stage_func(*args, **kwargs)
            self.results[stage_name] = {
                'success': True,
                'result': result,
                'error': None
            }
            print(f"\n✓ Stage '{stage_name}' completed successfully")
            return True

        except Exception as e:
            print(f"\n✗ Stage '{stage_name}' failed: {e}")
            self.results[stage_name] = {
                'success': False,
                'result': None,
                'error': str(e)
            }
            return False

    def stage_extract(self, pdf_path: Path = None):
        """Stage 1: Extract tables from PDFs"""
        dirs = self.config['directories']

        if pdf_path:
            return extract.extract_pdf(
                pdf_path,
                Path(dirs['extracted']),
                self.config['extraction']['pages']
            )
        else:
            return extract.extract_all_pdfs(
                Path(dirs['input']),
                Path(dirs['extracted'])
            )

    def stage_clean(self):
        """Stage 3: Clean extracted data"""
        dirs = self.config['directories']
        return clean.clean_all_tables(
            Path(dirs['extracted']),
            Path(dirs['cleaned'])
        )

    def stage_analyze(self):
        """Stage 2: Analyze extracted data (placeholder)"""
        print("Analysis stage - generating summary...")
        # Will implement when we move analyze.py
        return {'success': True, 'message': 'Analysis complete'}

    def stage_prepare_database(self):
        """Stage 4: Prepare database-ready format (placeholder)"""
        print("Database preparation stage...")
        # Will implement when we move prepare_db.py
        return {'success': True, 'message': 'Database preparation complete'}

    def run_full_pipeline(self, pdf_path: Path = None, start_from: str = None):
        """
        Run complete pipeline

        Args:
            pdf_path: Optional specific PDF to process
            start_from: Optional stage name to start from
        """
        stages = [
            ('extract', lambda: self.stage_extract(pdf_path)),
            ('clean', self.stage_clean),
            ('analyze', self.stage_analyze),
            ('prepare_database', self.stage_prepare_database),
        ]

        # Find starting point
        start_idx = 0
        if start_from:
            start_idx = next((i for i, (name, _) in enumerate(stages) if name == start_from), 0)
            if start_idx > 0:
                print(f"\nResuming pipeline from stage: {start_from}")

        # Run stages
        for stage_name, stage_func in stages[start_idx:]:
            success = self.run_stage(stage_name, stage_func)
            if not success:
                print(f"\n⚠ Pipeline stopped at stage '{stage_name}' due to error")
                break

        # Final summary
        self.print_summary()

    def print_summary(self):
        """Print pipeline execution summary"""
        elapsed = (datetime.now() - self.start_time).total_seconds()

        print("\n" + "="*80)
        print("PIPELINE SUMMARY")
        print("="*80)
        print(f"Total time: {elapsed:.1f}s")
        print(f"\nStages completed:")

        for stage_name, result in self.results.items():
            status = "✓" if result['success'] else "✗"
            print(f"  {status} {stage_name}")

        # Save results
        results_path = Path(self.config['directories']['output_base']) / 'pipeline_results.json'
        with open(results_path, 'w') as f:
            # Make results JSON-serializable
            json_results = {
                k: {'success': v['success'], 'error': v['error']}
                for k, v in self.results.items()
            }
            json.dump({
                'timestamp': self.start_time.isoformat(),
                'elapsed_seconds': elapsed,
                'results': json_results
            }, f, indent=2)

        print(f"\n✓ Pipeline results saved: {results_path}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Automated pipeline for processing solubility data from PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all PDFs in Data/ directory
  python pipeline.py --all

  # Process specific PDF
  python pipeline.py --pdf Data/SDS-31_Part1.pdf

  # Resume from cleaning stage
  python pipeline.py --all --start-from clean

  # Use custom configuration
  python pipeline.py --all --config custom_config.yaml
        """
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all PDFs in input directory'
    )
    parser.add_argument(
        '--pdf',
        type=Path,
        help='Process specific PDF file'
    )
    parser.add_argument(
        '--start-from',
        choices=['extract', 'clean', 'analyze', 'prepare_database'],
        help='Start pipeline from specific stage'
    )
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to configuration YAML file'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.all and not args.pdf:
        parser.error("Must specify either --all or --pdf")

    if args.pdf and not args.pdf.exists():
        print(f"Error: PDF file not found: {args.pdf}")
        return 1

    # Initialize and run pipeline
    print("="*80)
    print("SOLUBILITY DATA PROCESSING PIPELINE")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    pipeline = Pipeline(args.config)
    pipeline.run_full_pipeline(
        pdf_path=args.pdf if not args.all else None,
        start_from=args.start_from
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
