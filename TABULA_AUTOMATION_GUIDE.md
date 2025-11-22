# Tabula-Java Automation Guide

## Overview

This guide shows how to use the official **tabula-java** command-line tool for automated extraction of solubility data from SDS-31 PDFs.

**GitHub Repository**: https://github.com/tabulapdf/tabula-java

## Why Tabula-Java CLI?

✅ **Official tool** - Made by the Tabula team
✅ **Battle-tested** - Used in production by many organizations
✅ **Simple dependencies** - Only needs Java
✅ **Easy automation** - Works with bash/batch scripts
✅ **No Python required** - Standalone JAR file
✅ **Cross-platform** - Works on Linux, macOS, Windows

## Quick Start (2 Minutes)

### 1. Check Java Installation

```bash
java -version
```

If not installed:
- **Ubuntu/Debian**: `sudo apt-get install default-jre`
- **macOS**: `brew install openjdk`
- **Windows**: https://www.java.com/download/

### 2. Run the Automation Script

```bash
# Make script executable (Linux/macOS)
chmod +x extract_with_tabula.sh

# Extract pages 10-30 from Part 7 (default)
./extract_with_tabula.sh

# Or extract all pages
./extract_with_tabula.sh Data/SDS-31_Part7.pdf all

# Or process all PDFs
./extract_with_tabula.sh --all
```

The script will:
1. Auto-download tabula-java JAR (~65MB) on first run
2. Extract tables using three modes (lattice, stream, auto)
3. Save results as CSV files

## Manual Installation

### Download Tabula-Java

```bash
# Download latest release
wget https://github.com/tabulapdf/tabula-java/releases/download/v1.0.5/tabula-1.0.5-jar-with-dependencies.jar

# Or use curl
curl -L -O https://github.com/tabulapdf/tabula-java/releases/download/v1.0.5/tabula-1.0.5-jar-with-dependencies.jar
```

### Basic Usage

```bash
# Extract all tables from all pages
java -jar tabula-1.0.5-jar-with-dependencies.jar input.pdf

# Extract from specific pages
java -jar tabula-1.0.5-jar-with-dependencies.jar --pages 10-30 input.pdf

# Save to file
java -jar tabula-1.0.5-jar-with-dependencies.jar --pages 10-30 -o output.csv input.pdf

# Use lattice mode (for bordered tables)
java -jar tabula-1.0.5-jar-with-dependencies.jar --lattice --pages 10-30 -o output.csv input.pdf

# Use stream mode (for borderless tables)
java -jar tabula-1.0.5-jar-with-dependencies.jar --stream --pages 10-30 -o output.csv input.pdf
```

## Command-Line Options

### Essential Options

| Option | Description | Example |
|--------|-------------|---------|
| `-p, --pages` | Page range to extract | `--pages 10-30` or `--pages all` |
| `-o, --outfile` | Output file path | `-o output.csv` |
| `-l, --lattice` | Use lattice mode (bordered tables) | `--lattice` |
| `-t, --stream` | Use stream mode (borderless tables) | `--stream` |
| `-f, --format` | Output format (CSV, TSV, JSON) | `-f CSV` (default) |

### Advanced Options

| Option | Description | Example |
|--------|-------------|---------|
| `-a, --area` | Specific area to extract | `-a 0,0,100,500` |
| `-c, --columns` | Column boundaries | `-c 10,20,30` |
| `-g, --guess` | Auto-detect tables | `--guess` |
| `--spreadsheet` | Force spreadsheet mode | `--spreadsheet` |

## Automation Examples

### Example 1: Single File

```bash
#!/bin/bash
# Extract from one PDF

TABULA_JAR="tabula-1.0.5-jar-with-dependencies.jar"
INPUT_PDF="Data/SDS-31_Part7.pdf"
OUTPUT_FILE="extracted_data/part7_tables.csv"

java -jar "$TABULA_JAR" \
    --pages 10-30 \
    --lattice \
    --outfile "$OUTPUT_FILE" \
    "$INPUT_PDF"

echo "Extraction complete: $OUTPUT_FILE"
```

### Example 2: Batch Process All PDFs

```bash
#!/bin/bash
# Process all PDFs in Data/ directory

TABULA_JAR="tabula-1.0.5-jar-with-dependencies.jar"
DATA_DIR="Data"
OUTPUT_DIR="extracted_data"

mkdir -p "$OUTPUT_DIR"

for pdf_file in "$DATA_DIR"/*.pdf; do
    filename=$(basename "$pdf_file" .pdf)
    output_file="$OUTPUT_DIR/${filename}_tables.csv"

    echo "Processing: $pdf_file"

    java -jar "$TABULA_JAR" \
        --pages 10-50 \
        --lattice \
        --outfile "$output_file" \
        "$pdf_file"

    echo "  Saved to: $output_file"
done

echo "All PDFs processed!"
```

### Example 3: Multiple Modes

```bash
#!/bin/bash
# Try both lattice and stream modes

TABULA_JAR="tabula-1.0.5-jar-with-dependencies.jar"
INPUT_PDF="Data/SDS-31_Part7.pdf"
PAGES="10-30"

# Lattice mode (bordered tables)
java -jar "$TABULA_JAR" \
    --pages "$PAGES" \
    --lattice \
    --outfile "output_lattice.csv" \
    "$INPUT_PDF"

# Stream mode (borderless tables)
java -jar "$TABULA_JAR" \
    --pages "$PAGES" \
    --stream \
    --outfile "output_stream.csv" \
    "$INPUT_PDF"

echo "Compare results:"
echo "  Lattice: output_lattice.csv"
echo "  Stream:  output_stream.csv"
```

### Example 4: Specific Page Ranges

```bash
#!/bin/bash
# Extract different sections

TABULA_JAR="tabula-1.0.5-jar-with-dependencies.jar"
INPUT_PDF="Data/SDS-31_Part1.pdf"

# Extract evaluation texts
java -jar "$TABULA_JAR" --pages 1-50 -o evaluation.csv "$INPUT_PDF"

# Extract data tables
java -jar "$TABULA_JAR" --pages 51-150 -o data_tables.csv "$INPUT_PDF"

# Extract references
java -jar "$TABULA_JAR" --pages 151-200 -o references.csv "$INPUT_PDF"
```

## Getting Table Coordinates (Advanced)

For precise extraction, use the Tabula GUI to get exact coordinates:

1. Download Tabula GUI: https://tabula.technology/
2. Open your PDF
3. Select the table area you want
4. Under "Export Format", select **"Script"**
5. Click "Export"

The script will contain exact coordinates like:

```bash
java -jar tabula-java.jar \
    --pages 15 \
    --area 34.88,12.75,693.97,561.00 \
    --columns 28.28,280.18,483.17 \
    input.pdf
```

Use these coordinates in your automation script!

## Comparison with Python Approaches

| Feature | Tabula-Java CLI | Python (pdfplumber) | Python (camelot) |
|---------|----------------|---------------------|------------------|
| Installation | Java only | Python + deps | Python + Ghostscript |
| Dependencies | ✅ Minimal | Medium | Complex |
| Automation | ✅ Easy (bash) | Easy (Python) | Easy (Python) |
| Performance | ✅ Fast | Medium | Slow |
| Accuracy | Very Good | Very Good | Excellent |
| GUI support | ✅ Yes (separate) | No | No |
| Best for | Production automation | Python workflows | Highest accuracy |

## Troubleshooting

### Java Not Found

```bash
# Check if Java is installed
java -version

# Install Java
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install default-jre

# macOS
brew install openjdk

# Windows
# Download from https://www.java.com/download/
```

### Out of Memory Error

```bash
# Increase Java heap size
java -Xmx4g -jar tabula-1.0.5-jar-with-dependencies.jar input.pdf
```

### No Tables Found

Try different modes:
```bash
# Try lattice mode
java -jar tabula.jar --lattice input.pdf

# Try stream mode
java -jar tabula.jar --stream input.pdf

# Try auto-detect
java -jar tabula.jar --guess input.pdf
```

### Poor Quality Results

1. Use the GUI to find exact coordinates
2. Specify table area with `--area`
3. Specify columns with `--columns`
4. Try different extraction modes

## Production Deployment

### Docker Container

Create a `Dockerfile`:

```dockerfile
FROM openjdk:11-jre-slim

# Install dependencies
RUN apt-get update && apt-get install -y wget

# Download Tabula
WORKDIR /app
RUN wget https://github.com/tabulapdf/tabula-java/releases/download/v1.0.5/tabula-1.0.5-jar-with-dependencies.jar

# Copy extraction script
COPY extract_with_tabula.sh .
RUN chmod +x extract_with_tabula.sh

# Set up volumes
VOLUME ["/data", "/output"]

CMD ["./extract_with_tabula.sh", "--all"]
```

Build and run:
```bash
docker build -t solubility-extractor .
docker run -v $(pwd)/Data:/data -v $(pwd)/extracted_data:/output solubility-extractor
```

### Cron Job

Automate extraction on a schedule:

```bash
# Add to crontab (crontab -e)
0 2 * * * /path/to/extract_with_tabula.sh --all >> /var/log/extraction.log 2>&1
```

## Integration Examples

### With Make

Create a `Makefile`:

```makefile
TABULA_JAR = tabula-1.0.5-jar-with-dependencies.jar
DATA_DIR = Data
OUTPUT_DIR = extracted_data

.PHONY: all clean download

all: extract

download:
	wget -nc https://github.com/tabulapdf/tabula-java/releases/download/v1.0.5/$(TABULA_JAR)

extract: download
	mkdir -p $(OUTPUT_DIR)
	./extract_with_tabula.sh --all

clean:
	rm -rf $(OUTPUT_DIR)/*.csv
```

Usage:
```bash
make download  # Download Tabula JAR
make extract   # Extract all PDFs
make clean     # Remove output files
```

### With Python

Call from Python:

```python
import subprocess
import os

def extract_tables(pdf_path, pages="10-30", output_dir="extracted_data"):
    """Extract tables using tabula-java CLI"""

    jar_file = "tabula-1.0.5-jar-with-dependencies.jar"
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_file = f"{output_dir}/{pdf_name}_tables.csv"

    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "java", "-jar", jar_file,
        "--pages", pages,
        "--lattice",
        "--outfile", output_file,
        pdf_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✓ Extracted: {output_file}")
        return output_file
    else:
        print(f"✗ Error: {result.stderr}")
        return None

# Usage
extract_tables("Data/SDS-31_Part7.pdf", pages="all")
```

## Performance Tips

1. **Process in parallel** for multiple PDFs:
```bash
# GNU parallel
parallel java -jar tabula.jar --pages 10-30 -o {/.}.csv {} ::: Data/*.pdf
```

2. **Use specific pages** instead of "all":
```bash
# Faster
java -jar tabula.jar --pages 10-50 input.pdf

# Slower
java -jar tabula.jar --pages all input.pdf
```

3. **Increase Java heap** for large PDFs:
```bash
java -Xmx4g -jar tabula.jar input.pdf
```

## Summary

**For quick automation, use the provided script:**
```bash
./extract_with_tabula.sh --all
```

**For custom workflows:**
- Use tabula-java JAR directly
- Integrate with your existing scripts
- Deploy in Docker for reproducibility

**Advantages over other methods:**
- ✅ Simple, only needs Java
- ✅ Fast and reliable
- ✅ Easy to automate
- ✅ Official tool from Tabula team
- ✅ Production-ready

This is the **recommended approach** for automated solubility data extraction!
