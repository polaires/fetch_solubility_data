# Solubility Data Extraction Tool

Extract solubility data for binary aqueous systems from SDS-31 (Solubility Data Series - Alkali Metal Orthophosphates) PDF files.

## Overview

This repository contains PDFs from the **Solubility Data Series Volume 31** covering alkali metal orthophosphates. The PDFs contain:
- Evaluation texts (pages marked with E)
- Compiled solubility data tables
- Chemical compound data indexed by CAS registry numbers
- Author and registry number indexes

## Extraction Tools

The project uses three powerful PDF table extraction libraries:

1. **Camelot** - Best for tables with clear borders (lattice mode) and scientific documents
2. **Tabula** - Excellent for detecting tables in scientific documents
3. **pdfplumber** - Provides fine-grained control for complex tables

## Installation

### Prerequisites

- Python 3.8 or higher
- Ghostscript (required for Camelot)
- Java 8+ (required for Tabula)

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

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Camelot (Lattice)** | Tables with clear borders | Highest accuracy for bordered tables | Slower processing |
| **Camelot (Stream)** | Borderless tables | Good for tables without lines | May miss some structures |
| **Tabula** | Scientific documents | Fast, good detection | Requires Java |
| **pdfplumber** | Complex layouts | Fine control, no Java needed | May need custom settings |

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

## References

- IUPAC Solubility Data Series: https://iupac.org/what-we-do/databases/
- Camelot Documentation: https://camelot-py.readthedocs.io/
- Tabula Documentation: https://tabula-py.readthedocs.io/
- pdfplumber Documentation: https://github.com/jsvine/pdfplumber
