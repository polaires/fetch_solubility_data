#!/usr/bin/env python3
"""
Prepare data for Vercel deployment by copying CSV files into web-interface

This script copies cleaned CSV data into the web-interface directory
so it can be deployed to Vercel without relying on parent directory access.
"""

import shutil
from pathlib import Path
import json

def prepare_vercel_data():
    """Copy CSV files into web-interface for Vercel deployment"""

    # Paths - try nested structure first
    source_dir = Path("output/02_cleaned/cleaned_data")
    if not source_dir.exists():
        # Fallback to flat structure
        source_dir = Path("output/02_cleaned")

    if not source_dir.exists():
        print(f"❌ Error: Source directory not found: {source_dir}")
        print("Please run the extraction pipeline first:")
        print("  python pipeline.py --all")
        return

    dest_dir = Path("web-interface/public/data")

    # Create destination directory
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Get all CSV files (exclude manifests)
    csv_files = [f for f in source_dir.glob("*.csv") if "manifest" not in f.name.lower()]

    if not csv_files:
        print(f"❌ No CSV files found in {source_dir}")
        return

    print(f"Preparing {len(csv_files)} CSV files for Vercel deployment...")

    copied = 0
    for csv_file in csv_files:
        dest_file = dest_dir / csv_file.name
        shutil.copy2(csv_file, dest_file)
        copied += 1

        if copied % 50 == 0:
            print(f"  Copied {copied}/{len(csv_files)} files...")

    print(f"\n✓ Successfully copied {copied} CSV files to {dest_dir}")

    # Create a metadata file
    metadata = {
        "total_files": copied,
        "source_dir": str(source_dir),
        "prepared_for": "vercel_deployment",
        "data_location": "public/data/"
    }

    metadata_file = dest_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Created metadata file: {metadata_file}")

    # Calculate total size
    total_size = sum(f.stat().st_size for f in dest_dir.glob("*.csv"))
    print(f"\nTotal data size: {total_size / 1024 / 1024:.2f} MB")

    print("\n" + "="*60)
    print("NEXT STEPS FOR VERCEL DEPLOYMENT")
    print("="*60)
    print("1. Commit the changes:")
    print("   git add web-interface/public/data")
    print("   git commit -m 'Add data for Vercel deployment'")
    print("")
    print("2. Set Root Directory in Vercel Dashboard:")
    print("   Settings → General → Root Directory → 'web-interface'")
    print("")
    print("3. Or deploy from web-interface:")
    print("   cd web-interface")
    print("   vercel")

if __name__ == "__main__":
    prepare_vercel_data()
