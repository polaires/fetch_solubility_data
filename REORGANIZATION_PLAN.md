# Repository Reorganization Plan

## Goal
Create a clean, automated pipeline for processing solubility data from PDF booklets, ready to handle future booklets with minimal manual intervention.

## New Directory Structure

```
fetch_solubility_data/
├── README.md                    # Updated main documentation
├── requirements.txt             # Python dependencies
├── config.yaml                  # Configuration for processing
├── pipeline.py                  # Main automated pipeline (single command)
│
├── Data/                        # Input PDFs (unchanged)
│   ├── SDS-31_Part1.pdf
│   ├── SDS-31_Part2.pdf
│   └── ...
│
├── scripts/                     # Processing scripts (numbered workflow)
│   ├── extract.py              # 1. PDF table extraction
│   ├── analyze.py              # 2. Data analysis and quality check
│   ├── clean.py                # 3. OCR cleaning and standardization
│   ├── prepare_db.py           # 4. Database preparation and merging
│   └── utils.py                # Shared utility functions
│
├── output/                      # All generated outputs (organized by stage)
│   ├── 01_extracted/           # Raw CSV tables from PDFs
│   ├── 02_cleaned/             # OCR-cleaned tables
│   ├── 03_analyzed/            # Analysis reports and summaries
│   └── 04_database/            # Final database-ready files
│
├── docs/                        # Documentation
│   ├── EXTRACTION_RESULTS.md
│   ├── DATABASE_PREPARATION_STATUS.md
│   ├── QUICK_START.md
│   └── INSTALLATION_GUIDE.md
│
└── archive/                     # Old/test scripts (for reference)
    ├── test_tabula.py
    ├── simple_extract.py
    └── ...
```

## Automation Features

### 1. Single Command Processing
```bash
# Process all PDFs in Data/ directory
python pipeline.py --process-all

# Process specific PDF
python pipeline.py --pdf Data/SDS-31_Part1.pdf

# Process new booklet
python pipeline.py --pdf Data/NewBooklet.pdf --name "NewBooklet"
```

### 2. Configuration File (config.yaml)
```yaml
extraction:
  multiple_tables: true
  pages: "all"

cleaning:
  ocr_fixes:
    - {from: "mo1", to: "mol"}
    - {from: "I I", to: "II"}

database:
  merge_sequences: true
  validate_ranges: true
  export_formats: ["csv", "json", "sqlite"]
```

### 3. Modular Pipeline Stages
- Each stage can run independently
- Resume from any stage
- Skip completed stages

### 4. Automatic Quality Checks
- Validate extraction success
- Check data quality scores
- Flag tables needing review

### 5. Reporting
- Automatic summary generation
- Quality metrics
- Processing logs

## Migration Steps

1. **Create new directory structure**
   - Create scripts/, output/, docs/, archive/

2. **Consolidate scripts**
   - Merge extraction scripts → scripts/extract.py
   - Merge analysis scripts → scripts/analyze.py
   - Create clean.py with all cleaning functions
   - Update prepare_database.py → scripts/prepare_db.py
   - Extract common functions → scripts/utils.py

3. **Move existing files**
   - Move docs to docs/
   - Move test scripts to archive/
   - Move data directories to output/

4. **Create automation**
   - Build pipeline.py (main entry point)
   - Create config.yaml

5. **Update documentation**
   - Update README.md with new workflow
   - Add usage examples

6. **Test pipeline**
   - Run on existing data
   - Verify outputs match

## Benefits

✅ **Easy to use**: Single command to process new booklets
✅ **Organized**: Clear structure, easy to find files
✅ **Reproducible**: Configuration-driven processing
✅ **Scalable**: Ready for 10s or 100s of booklets
✅ **Maintainable**: Modular scripts, shared utilities
✅ **Professional**: Clean repo structure for collaboration

## Timeline

- Structure creation: 15 min
- Script consolidation: 30 min
- Pipeline implementation: 30 min
- Testing: 15 min
- Documentation: 15 min

**Total: ~2 hours**
