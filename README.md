# Solubility Data Extraction Tool

Extract solubility data for binary aqueous systems from SDS-31 (Solubility Data Series - Alkali Metal Orthophosphates) PDF files.

## 🚀 Quick Start (Recommended)

### Automated Extraction with Tabula-Java CLI

**The fastest and most reliable method for automation!**

```bash
# Linux/macOS
chmod +x extract_with_tabula.sh
./extract_with_tabula.sh

# Windows
extract_with_tabula.bat
```

This script will:
1. ✅ Auto-download tabula-java (~65MB) on first run
2. ✅ Extract tables using multiple modes (lattice, stream, auto)
3. ✅ Save results as CSV files
4. ✅ Only requires Java (no complex Python dependencies)

**See [TABULA_AUTOMATION_GUIDE.md](TABULA_AUTOMATION_GUIDE.md) for full details.**

## Overview

This repository contains PDFs from the **Solubility Data Series Volume 31** covering alkali metal orthophosphates. The PDFs contain:
- Evaluation texts (pages marked with E)
- Compiled solubility data tables
- Chemical compound data indexed by CAS registry numbers
- Author and registry number indexes

## Extraction Methods

### 🥇 Method 1: Tabula-Java CLI (RECOMMENDED)

**GitHub**: https://github.com/tabulapdf/tabula-java

**Why this is best:**
- ✅ Official tool from Tabula team
- ✅ Only needs Java (simple dependency)
- ✅ Battle-tested and production-ready
- ✅ Easy automation with bash/batch scripts
- ✅ Fast and reliable

**Usage:**
```bash
./extract_with_tabula.sh --all          # Process all PDFs
./extract_with_tabula.sh [pdf] [pages]  # Custom extraction
```

### 🥈 Method 2: Python Tools

The project also includes Python-based extraction using:

1. **Camelot** - Best for tables with clear borders (lattice mode)
2. **Tabula-py** - Python wrapper for Tabula
3. **pdfplumber** - Fine-grained control for complex tables

## Installation

### For Tabula-Java CLI (Recommended)

**Prerequisites:**
- Java 8 or higher

**Check Java:**
```bash
java -version
```

**Install Java if needed:**
- Ubuntu/Debian: `sudo apt-get install default-jre`
- macOS: `brew install openjdk`
- Windows: https://www.java.com/download/

**That's it!** The script auto-downloads the JAR file on first run.

### For Python Tools (Optional)

**Prerequisites:**
- Python 3.8 or higher
- Ghostscript (required for Camelot)
- Java 8+ (required for Tabula-py)

### Install Ghostscript

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ghostscript
```

**macOS:**
```bash
brew install ghostscript
```

**Windows:**
Download from https://ghostscript.com/releases/gsdnld.html

### Install Java (for Tabula)

**Ubuntu/Debian:**
```bash
sudo apt-get install default-jre
```

**macOS:**
```bash
brew install openjdk
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Extraction

Extract tables from the smallest PDF (Part 7):

```bash
python extract_solubility_data.py
```

### Advanced Usage

Edit the script to customize extraction:

```python
# Extract from all pages
results = extractor.extract_all(pages='all')

# Extract from specific pages
results = extractor.extract_all(pages='10-30')

# Extract from multiple page ranges
results = extractor.extract_all(pages='10-30,50-70')

# Use specific extraction methods only
results = extractor.extract_all(
    pages='all',
    methods=['camelot_lattice', 'pdfplumber']
)
```

### Extract from a Specific PDF

```python
from extract_solubility_data import SolubilityDataExtractor

# Extract from Part 1
extractor = SolubilityDataExtractor("Data/SDS-31_Part1.pdf")
results = extractor.extract_all(pages='all')
```

## Output

Extracted tables are saved as CSV files in the `extracted_data/` directory:

```
extracted_data/
├── SDS-31_Part7_camelot_lattice_table_1.csv
├── SDS-31_Part7_camelot_stream_table_1.csv
├── SDS-31_Part7_tabula_table_1.csv
└── SDS-31_Part7_pdfplumber_table_1.csv
```

## Comparison of Methods

| Method | Installation | Dependencies | Speed | Accuracy | Best For |
|--------|--------------|--------------|-------|----------|----------|
| **Tabula-Java CLI** ⭐ | Easy | Java only | Fast | Very Good | Production automation |
| **pdfplumber** | Easy | Python + deps | Medium | Very Good | Python workflows |
| **Camelot (Lattice)** | Hard | Python + Ghostscript | Slow | Excellent | Highest accuracy needs |
| **Tabula-py** | Medium | Python + Java | Fast | Very Good | Python + Java users |
| **Online Tabula** | None | Browser | N/A | Good | Quick testing |

## Recommended Workflow

1. **Test extraction** on a small PDF section (pages 10-30)
2. **Compare results** from different methods
3. **Identify the best method** for your specific tables
4. **Apply to all PDFs** using the best-performing method
5. **Validate and clean** the extracted data

## Alternative Online Tools

If you prefer online tools or need OCR capabilities for scanned PDFs:

1. **Tabula (Web version)** - https://tabula.technology/
   - Free, open-source
   - No installation needed
   - Limited to smaller files

2. **Camelot Web** - Can be deployed as a web service
   - See: https://github.com/camelot-dev/excalibur

3. **ABBYY FineReader** - Commercial OCR solution
   - Excellent for scanned documents
   - Requires license

4. **Adobe Acrobat Pro** - Export tables to Excel
   - Good accuracy
   - Requires subscription

5. **ChemDataExtractor** - Specialized for chemistry data
   - https://github.com/CambridgeMolecularEngineering/ChemDataExtractor
   - Built for scientific literature

## Data Structure

The SDS-31 PDFs contain:

- **Registry Number Index**: CAS numbers with page references
- **Author Index**: Publications indexed by author
- **Evaluation Texts**: Pages prefixed with 'E'
- **Compiled Tables**: Solubility data tables
- **Binary Aqueous Systems**: Water + compound solubility data

## Troubleshooting

### Camelot not working
```bash
# Install system dependencies
sudo apt-get install python3-tk ghostscript
pip install 'camelot-py[cv]'
```

### Tabula not working
```bash
# Check Java installation
java -version

# If not installed
sudo apt-get install default-jre
```

### Out of memory for large PDFs
- Process pages in smaller batches
- Use stream mode instead of lattice
- Increase system swap space

## Contributing

To add support for more extraction methods or improve accuracy:

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

## License

This tool is provided for research and educational purposes. The SDS-31 PDF data is subject to IUPAC copyright.

## Documentation

- **[TABULA_AUTOMATION_GUIDE.md](TABULA_AUTOMATION_GUIDE.md)** - Complete guide for tabula-java automation
- **[QUICK_START.md](QUICK_START.md)** - Get started in 3 minutes
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - Detailed installation instructions
- **[SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md)** - Overview and recommendations

## References

- **Tabula-Java**: https://github.com/tabulapdf/tabula-java (Official CLI tool)
- **Tabula Online**: https://tabula.technology/ (Web interface)
- IUPAC Solubility Data Series: https://iupac.org/what-we-do/databases/
- Camelot Documentation: https://camelot-py.readthedocs.io/
- Tabula-py Documentation: https://tabula-py.readthedocs.io/
- pdfplumber Documentation: https://github.com/jsvine/pdfplumber
