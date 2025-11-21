# Solubility Data Extraction & Processing

Automated pipeline for extracting and processing binary aqueous solubility data from PDF booklets (specifically IUPAC SDS-31: Alkali Metal Orthophosphates).

## 🚀 Quick Start

### Process All PDFs

```bash
# Install dependencies
pip install -r requirements.txt

# Run automated pipeline
python pipeline.py --all
```

That's it! The pipeline will:
1. Extract all tables from PDFs in `Data/` directory
2. Clean OCR artifacts
3. Analyze data quality
4. Prepare database-ready format

### Process Single PDF

```bash
python pipeline.py --pdf Data/SDS-31_Part1.pdf
```

### Process New Booklet

Simply add your new PDF to the `Data/` directory and run:

```bash
python pipeline.py --all
```

## 📁 Repository Structure

```
fetch_solubility_data/
├── pipeline.py              # ⭐ Main automated pipeline (start here!)
├── config.yaml              # Configuration file
├── requirements.txt         # Python dependencies
│
├── Data/                    # Input: PDF files
│   ├── SDS-31_Part1.pdf    # (7 PDF files total)
│   └── ...
│
├── scripts/                 # Processing modules
│   ├── extract.py          # PDF table extraction (tabula-py)
│   ├── clean.py            # OCR artifact cleaning
│   ├── analyze.py          # Data analysis (coming soon)
│   ├── prepare_db.py       # Database preparation (coming soon)
│   └── utils.py            # Shared utilities
│
├── output/                  # Generated outputs (organized by stage)
│   ├── 01_extracted/       # Raw extracted CSVs (338 files)
│   ├── 02_cleaned/         # Cleaned tables
│   ├── 03_analyzed/        # Analysis reports
│   └── 04_database/        # Database-ready files
│
├── docs/                    # Documentation
│   ├── EXTRACTION_RESULTS.md
│   ├── DATABASE_PREPARATION_STATUS.md
│   └── ...
│
└── archive/                 # Legacy/test scripts (for reference)
```

## 🔧 Advanced Usage

### Resume from Specific Stage

If pipeline stops or you want to reprocess from a certain point:

```bash
# Skip extraction, start from cleaning
python pipeline.py --all --start-from clean

# Start from analysis
python pipeline.py --all --start-from analyze
```

### Custom Configuration

Create your own config file:

```bash
# Copy default config
cp config.yaml my_config.yaml

# Edit settings
nano my_config.yaml

# Run with custom config
python pipeline.py --all --config my_config.yaml
```

### Run Individual Stages

```bash
# Only extract tables
python scripts/extract.py --pdf-dir Data --output output/01_extracted

# Only clean data
python scripts/clean.py --input output/01_extracted --output output/02_cleaned
```

## 📊 Current Results (SDS-31 Booklet)

Successfully processed **7 PDF files** (SDS-31 Parts 1-7):

- ✅ **338 tables** extracted
- ✅ **5,930 rows** of solubility data
- ✅ **32,905 numeric values**
- ✅ **71% of tables** contain phase information
- ✅ **31% of tables** contain mass% data
- ✅ **24% of tables** contain molality data

### Data Types Extracted

- 🔬 Phase diagrams (A, B, C, D, E, F phases)
- 📊 Mass percent (mass%)
- 📈 Molality (mol/kg H₂O)
- 🧪 Mole percent (mol%)
- 🌡️ Temperature data (°C and K)

See `docs/EXTRACTION_RESULTS.md` for detailed analysis.

## 🛠️ Pipeline Stages

### 1. Extraction (`scripts/extract.py`)
- Uses **tabula-py** to extract tables from PDFs
- Saves each table as CSV with metadata
- Generates extraction manifest

### 2. Cleaning (`scripts/clean.py`)
- Fixes OCR artifacts automatically:
  - `0 . 015` → `0.015` (spaces in numbers)
  - `0,016` → `0.016` (comma as decimal)
  - `mo1/kg` → `mol/kg` (1 vs l confusion)
  - `I I` → `II` (split Roman numerals)
  - `Q .` → `0.` (letter O vs zero)

### 3. Analysis (`scripts/analyze.py`)
- Identifies data types in each table
- Quality scoring
- Generates summary reports

### 4. Database Preparation (`scripts/prepare_db.py`)
- Merges related table sequences
- Extracts phase markers from values
- Creates database-ready format
- Validates data ranges

## 🔬 Understanding the Data

### Phase Labels

Phase labels indicate different solid phases in equilibrium:

- **Single letters (A, B, C, D, E, F)**: Different solid phases
  - Different crystal structures (polymorphs)
  - Different hydration states (e.g., Na₃PO₄·12H₂O vs Na₃PO₄·10H₂O)

- **Roman numerals (II, III)**: Additional polymorphic forms

- **Combinations (A+B, B+C)**: Two-phase equilibrium regions
  - Two solid phases coexisting

### Concentration Units

- **mass%**: Mass percent of component in solution
- **mol%**: Mole percent
- **mol/kg H₂O**: Molality (moles per kg of water)
- **mole fraction**: x(component)

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# Input/output directories
directories:
  input: Data
  output_base: output

# Extraction parameters
extraction:
  pages: all                     # Or "1-10", "20-30"
  multiple_tables: true

# OCR fixes
cleaning:
  ocr_fixes:
    - {from: "mo1", to: "mol"}
    - {from: "I I", to: "II"}

# Export formats
database:
  export_formats: [csv, json, sqlite]
```

## 📚 Documentation

- **`docs/EXTRACTION_RESULTS.md`** - Extraction statistics and data quality analysis
- **`docs/DATABASE_PREPARATION_STATUS.md`** - Database preparation guide and issues
- **`REORGANIZATION_PLAN.md`** - Repository structure and automation details

## 🐛 Troubleshooting

### "No tables extracted"

- Check if PDF contains actual tables (not just text/images)
- Try adjusting `pages` parameter in config.yaml
- Some PDFs may require different tabula settings

### "OCR artifacts still present"

- Add new patterns to `ocr_fixes` in config.yaml
- Run cleaning stage again: `python scripts/clean.py`

### "Pipeline fails at specific stage"

- Check error message in console
- Check `output/pipeline.log` for details
- Resume from previous stage: `--start-from <stage>`

### Java not found (for tabula)

```bash
# Ubuntu/Debian
sudo apt-get install default-jre

# macOS
brew install openjdk

# Check installation
java -version
```

## 📝 Requirements

- Python 3.8+
- **tabula-py** (PDF extraction)
- **pandas** (data processing)
- **PyYAML** (configuration)
- **Java 8+** (required by tabula)

See `requirements.txt` for complete list.

## 🚀 Future Enhancements

- [ ] Automatic chemical system identification
- [ ] Column header standardization
- [ ] Temperature data extraction and normalization
- [ ] SQLite database export
- [ ] Web interface for browsing data
- [ ] REST API for querying solubility data
- [ ] Support for additional booklet types

## 🤝 Contributing

To add support for new booklet types:

1. Place PDF in `Data/` directory
2. Run pipeline: `python pipeline.py --all`
3. Check extraction quality in `output/01_extracted/`
4. Adjust config if needed
5. Report any issues or submit improvements via GitHub

## 📖 References

- **IUPAC Solubility Data Series**: https://iupac.org/what-we-do/databases/
- **SDS-31**: Alkali Metal Orthophosphates solubility data
- **tabula-py Documentation**: https://tabula-py.readthedocs.io/
- **Related Paper**: [cite original IUPAC publication]

## 📄 License

This tool is provided for research and educational purposes. The SDS-31 PDF data is subject to IUPAC copyright. Please cite original sources when using the extracted data.

---

**Last Updated**: 2025-11-21
**Pipeline Version**: 1.0.0
**Status**: Production-ready for SDS-31, extensible for other booklets
