# Installation Guide for Solubility Data Extraction

## Recommended Approach: Use Online Tools First

Given the complexity of PDF table extraction and potential dependency conflicts, here are the recommended approaches:

## Option 1: Online Tools (Easiest - No Installation)

### Tabula (Web Version) - **RECOMMENDED FOR BEGINNERS**

1. Visit: https://tabula.technology/
2. Upload your PDF (SDS-31_Part7.pdf is smallest at 15MB)
3. Select the pages you want to extract (e.g., pages 10-30)
4. Draw boxes around the tables you want to extract
5. Click "Preview & Export Data"
6. Download as CSV

**Pros:**
- No installation required
- Visual interface to select tables
- Free and open-source
- Works in browser

**Cons:**
- Limited to smaller files (may need to split large PDFs)
- Manual table selection
- Requires internet connection

### PDFTables.com

1. Visit: https://pdftables.com/
2. Upload PDF
3. Automatically extracts tables
4. Free for first few conversions

## Option 2: Docker (Recommended for Reproducibility)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ghostscript \
    libpoppler-cpp-dev \
    python3-tk \
    default-jre \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

CMD ["python", "extract_solubility_data.py"]
```

Run with:
```bash
docker build -t solubility-extractor .
docker run -v $(pwd)/Data:/app/Data -v $(pwd)/extracted_data:/app/extracted_data solubility-extractor
```

## Option 3: Local Installation (Advanced)

### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
# Update package lists
sudo apt-get update

# Install Ghostscript (for Camelot)
sudo apt-get install -y ghostscript

# Install Java (for Tabula)
sudo apt-get install -y default-jre

# Install additional dependencies
sudo apt-get install -y python3-tk libpoppler-cpp-dev
```

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install ghostscript
brew install openjdk
brew install poppler
```

**Windows:**
1. Download and install Ghostscript: https://ghostscript.com/releases/gsdnld.html
2. Download and install Java: https://www.java.com/download/
3. Add both to your PATH environment variable

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

### Step 3: Install Python Packages

Try installing packages one at a time to identify issues:

```bash
# Install pandas first
pip install pandas

# Install pdfplumber (simplest, fewest dependencies)
pip install pdfplumber

# Install tabula-py (requires Java)
pip install tabula-py

# Install camelot-py (requires Ghostscript)
pip install 'camelot-py[base]'
pip install opencv-python-headless
```

### Step 4: Verify Installation

```bash
python -c "import pdfplumber; print('pdfplumber OK')"
python -c "import tabula; print('tabula OK')"
python -c "import camelot; print('camelot OK')"
```

## Option 4: Use Specialized Chemistry Tools

### ChemDataExtractor

For chemistry-specific PDF extraction:

```bash
pip install chemdataextractor
```

Example usage:
```python
from chemdataextractor import Document

# Extract from PDF
doc = Document.from_file('Data/SDS-31_Part7.pdf')

# Extract tables
for table in doc.tables:
    print(table)
```

## Option 5: Manual Extraction with Adobe/LibreOffice

1. **Adobe Acrobat Pro** (Commercial):
   - Open PDF
   - File → Export To → Spreadsheet → Excel
   - Tables are automatically detected

2. **LibreOffice Draw** (Free):
   - Open PDF in LibreOffice Draw
   - Select and copy tables
   - Paste into LibreOffice Calc
   - Export as CSV

## Troubleshooting Common Issues

### Issue: `ModuleNotFoundError: No module named '_cffi_backend'`

**Solution:**
```bash
pip install --upgrade cffi
```

### Issue: Camelot fails with `Ghostscript not found`

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install ghostscript

# macOS
brew install ghostscript

# Verify installation
gs --version
```

### Issue: Tabula fails with `Java not found`

**Solution:**
```bash
# Check Java installation
java -version

# If not installed (Ubuntu/Debian)
sudo apt-get install default-jre

# If not installed (macOS)
brew install openjdk
```

### Issue: Out of memory when processing large PDFs

**Solution 1:** Process pages in smaller batches
```python
# Instead of pages='all'
results = extractor.extract_all(pages='1-50')
results = extractor.extract_all(pages='51-100')
# etc.
```

**Solution 2:** Use stream mode instead of lattice
```python
results = extractor.extract_with_camelot(flavor='stream')
```

### Issue: Extracted tables have poor quality

**Solutions:**
1. Try different extraction methods (pdfplumber vs camelot vs tabula)
2. Adjust table detection settings
3. Use the online Tabula tool for manual table selection
4. Consider OCR if PDF is scanned (use tesseract)

## Dependency Conflicts in System Python

If you encounter conflicts with system-installed packages:

1. **Always use a virtual environment**
2. **Or use Docker** (recommended for production)
3. **Or use conda** instead of pip:

```bash
conda create -n solubility python=3.11
conda activate solubility
conda install pandas
pip install pdfplumber tabula-py 'camelot-py[base]'
```

## Minimal Installation (Just pdfplumber)

If you only want to try one tool:

```bash
pip install pdfplumber pandas
python quick_extract.py
```

This uses only pdfplumber, which has the fewest system dependencies.

## Cloud-Based Solutions

### Google Colab (Free)

Create a notebook at https://colab.research.google.com/:

```python
# Install dependencies
!pip install pdfplumber pandas

# Upload your PDF
from google.colab import files
uploaded = files.upload()

# Extract tables
import pdfplumber
import pandas as pd

with pdfplumber.open('SDS-31_Part7.pdf') as pdf:
    for page in pdf.pages[:10]:  # First 10 pages
        tables = page.extract_tables()
        for table in tables:
            df = pd.DataFrame(table[1:], columns=table[0])
            print(df)
```

## Summary: Which Option Should You Choose?

| Use Case | Recommended Option |
|----------|-------------------|
| Just want to test quickly | Online Tabula (https://tabula.technology/) |
| Need reproducible setup | Docker |
| Working on local machine | Virtual environment + pdfplumber |
| Need best accuracy | Install all three tools (camelot, tabula, pdfplumber) |
| Have dependency issues | Use Google Colab or Docker |
| Processing many PDFs | Docker or properly configured local environment |

## Getting Help

If you encounter issues:

1. Check the error message carefully
2. Verify system dependencies are installed (Java, Ghostscript)
3. Try using a virtual environment
4. Consider using Docker for a clean environment
5. Use online tools as a fallback
