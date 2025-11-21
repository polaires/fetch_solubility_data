# Quick Start Guide

## 🎯 Goal
Extract solubility data tables from SDS-31 PDF files for binary aqueous systems.

## 📊 What's in the PDFs?

The SDS-31 (Solubility Data Series Volume 31) contains:
- **Subject**: Alkali Metal Orthophosphates solubility data
- **Content**: Compiled tables + evaluation texts
- **Data Type**: Binary aqueous systems (water + chemical compound)
- **Format**: Tables with temperature, concentration, and solubility values

## 🚀 Fastest Way to Extract Data (3 minutes)

### Method 1: Online Tabula (No Installation!)

1. Go to: **https://tabula.technology/**
2. Click "Upload" and select `Data/SDS-31_Part7.pdf` (smallest file, 15MB)
3. Tabula will show you the PDF pages
4. Click on pages with tables (skip index pages at the beginning)
5. Draw boxes around the tables you want
6. Click "Preview & Export Data" → Choose "CSV"
7. Download your CSV files ✅

**Tip**: Start with pages 10-30 where the actual data tables begin.

## 📋 Understanding the PDF Structure

Based on analyzing SDS-31_Part7.pdf:

### Page Types:
1. **Registry Number Index** (pages 1-2): CAS number → page references
2. **Author Index** (pages 3-7): Research papers indexed by author
3. **Evaluation Texts** (pages with 'E' prefix like E1-E324): Analysis and discussion
4. **Compiled Tables** (numbered pages): The actual solubility data

### What to Extract:
- **Target**: Compiled table pages (without 'E' prefix)
- **Contains**: Temperature, concentration, solubility values
- **Skip**: Index pages, evaluation pages (unless you need the analysis)

## 🛠️ Using the Python Scripts (After Installation)

### Option A: Quick Test (Recommended First)

```bash
# Install minimal dependencies
pip install pdfplumber pandas

# Run quick extraction
python quick_extract.py
```

This will:
- Check what tools you have installed
- Extract tables from pages 10-20 of Part 7
- Save CSV files to `extracted_data/`

### Option B: Full Extraction

```bash
# Install all tools (see INSTALLATION_GUIDE.md)
pip install -r requirements.txt

# Run full extraction
python extract_solubility_data.py
```

This will:
- Use multiple extraction methods
- Compare results from different tools
- Extract from configurable page ranges

## 📝 Example: Manual Python Extraction

If you want a simple custom script:

```python
import pdfplumber
import pandas as pd
from pathlib import Path

# Open the PDF
pdf_path = "Data/SDS-31_Part7.pdf"
output_dir = Path("my_extracted_tables")
output_dir.mkdir(exist_ok=True)

with pdfplumber.open(pdf_path) as pdf:
    # Extract from pages 10-30 (where data tables typically are)
    for page_num in range(9, 30):  # 0-indexed, so 9 = page 10
        page = pdf.pages[page_num]
        tables = page.extract_tables()

        for i, table in enumerate(tables):
            if not table or len(table) < 2:
                continue

            # Convert to DataFrame
            # First row is usually the header
            df = pd.DataFrame(table[1:], columns=table[0])

            # Save to CSV
            filename = f"page{page_num+1}_table{i+1}.csv"
            df.to_csv(output_dir / filename, index=False)
            print(f"Saved: {filename} ({len(df)} rows)")

print(f"\nDone! Check the '{output_dir}' folder for your CSV files.")
```

Save this as `simple_extract.py` and run:
```bash
pip install pdfplumber pandas
python simple_extract.py
```

## 🎯 Recommended Workflow

### Step 1: Analyze (5 minutes)
Look at the PDF to understand:
- Which pages have tables?
- What do the tables look like?
- Are they bordered or borderless?

### Step 2: Test Extract (5 minutes)
Use online Tabula or `quick_extract.py` to extract a few tables

### Step 3: Validate (5 minutes)
Check the CSV files:
- Are columns correct?
- Is data complete?
- Any formatting issues?

### Step 4: Full Extract (varies)
Once you know what works:
- Apply to all PDF files
- Use the best-performing extraction method
- Adjust parameters as needed

## 📦 What You'll Get

After extraction, you'll have CSV files like:

```
extracted_data/
├── table_page10_1.csv
├── table_page11_1.csv
├── table_page12_1.csv
└── ...
```

Each CSV contains solubility data with columns like:
- Temperature (°C or K)
- Concentration (mol/L or g/100g)
- Compound name
- Solubility values
- References

## ⚠️ Common Issues

### "No tables found"
- You might be on index/evaluation pages
- Try different page ranges
- Some tables may need manual selection (use online Tabula)

### "Garbled data in CSV"
- The PDF might have complex formatting
- Try different extraction methods
- Manual adjustment may be needed

### "Installation errors"
- Use Docker (see INSTALLATION_GUIDE.md)
- Or use online tools (no installation needed!)
- Or use Google Colab

## 🔍 Finding Specific Data

To find solubility data for a specific compound:

1. **Check Registry Index** (PDF pages 1-2)
   - Find your compound's CAS number
   - Note the page references

2. **Go to those pages**
   - 'E' pages = evaluation/discussion
   - Number pages = data tables

3. **Extract those specific pages**
   ```python
   # Example: Extract pages 50-60
   extractor.extract_all(pages='50-60')
   ```

## 📚 All 7 PDF Parts

| File | Size | Content |
|------|------|---------|
| Part 1 | 37 MB | Compounds with CAS 57-13-6 to... |
| Part 2 | 39 MB | ... |
| Part 3 | 38 MB | ... |
| Part 4 | 37 MB | ... |
| Part 5 | 36 MB | ... |
| Part 6 | 35 MB | ... |
| Part 7 | 15 MB | Compounds with CAS ...to 101917-67-3 |

**Tip**: Start with Part 7 (smallest) for testing!

## ✅ Next Steps After Extraction

1. **Clean the data**: Remove empty rows, fix headers
2. **Merge tables**: Combine data from multiple tables if needed
3. **Convert units**: Standardize temperature/concentration units
4. **Validate**: Cross-check with original PDF
5. **Analyze**: Use the data for your research!

## 🆘 Getting Help

1. **Read**: INSTALLATION_GUIDE.md for detailed setup
2. **Read**: README.md for full documentation
3. **Try**: Online tools first (easiest!)
4. **Ask**: Create an issue on GitHub with your specific problem

## 💡 Pro Tips

1. **Start small**: Test on 10-20 pages before processing whole PDFs
2. **Use online tools first**: They work immediately, no setup needed
3. **Compare methods**: Different tools work better for different table formats
4. **Keep originals**: Always verify extracted data against the PDF
5. **Automate validation**: Write scripts to check data quality

---

**Ready to start?** Try the online Tabula tool now: https://tabula.technology/
