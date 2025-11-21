# Extraction Accuracy Report

**Date:** 2025-11-21
**Analysis Scope:** 100 tables from SDS-31 Parts 1-3

---

## Executive Summary

**Current Overall Accuracy: 63.6%**

The extraction pipeline successfully extracts tabular data from PDFs but faces significant challenges with header detection. While numeric data extraction and column separation are highly effective, 100% of tables lack meaningful column headers.

---

## Detailed Quality Metrics

### 1. Header Quality: 0.0%

**Problem:** All extracted tables have auto-generated numeric headers (`"0"`, `"1"`, `"2"`, etc.) instead of meaningful column names like "Temperature", "Composition", "Phase".

**Impact:**
- Users cannot understand what each column represents
- Searching by column name is impossible
- Data interpretation requires manual inspection

**Examples:**
```
SDS-31_Part1_table_007.csv:
  Headers: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
  Should be: ['Temperature (°C)', 'Mass %', 'Molality', 'Phase', ...]
```

### 2. Data Completeness: 77.3%

**Status:** Good, but 32% of tables have high null rates (>30% empty cells)

**Breakdown:**
- 68 tables have >70% data completeness (Good)
- 32 tables have <70% data completeness (Problematic)

**Causes of null values:**
- Sparse data in original PDFs (legitimate nulls)
- Failed cell extraction (extraction errors)
- Merged cells not properly handled
- Page boundaries cutting off data

### 3. Column Separation: 99.9%

**Status:** Excellent - no merged column issues detected

This metric indicates tabula-py is successfully identifying column boundaries and not merging adjacent columns together.

### 4. Numeric Accuracy: 77.4%

**Status:** Good - numeric values are being parsed correctly

**What's working:**
- OCR cleaning fixed 205+ comma decimal errors (`,` → `.`)
- Character confusion corrections (O→0, l→1)
- Whitespace normalization

**What's not captured:**
- Some numeric values have embedded phase labels (handled by our phase extractor)
- Scientific notation occasionally malformed
- Temperature symbols sometimes included in values

### 5. Overall Score: 63.6%

The overall score is the average of the four metrics above. The primary drag on the score is the 0% header quality.

---

## Comparison of Extraction Methods

Tested three different tabula-py extraction modes across multiple pages:

| Method | Average Quality | Notes |
|--------|----------------|-------|
| DEFAULT | 79.7% | Standard extraction with auto-detection |
| STREAM | 79.7% | Text-based extraction (no lines) |
| GUESS | 79.7% | Auto-detect between lattice/stream |

**Conclusion:** All methods perform similarly for this dataset. The current DEFAULT mode is appropriate.

**Note:** LATTICE mode was not fully tested due to processing time but may improve results for tables with clear grid lines.

---

## Common Issues

### Issue 1: Header Problems (100% of tables)

**Why this happens:**
- PDFs don't have explicit header rows
- Tabula interprets first data row as data, not headers
- No semantic understanding of table structure

**Current workaround:**
- Column type detection heuristics (implemented in enhanced pipeline)
- Infers column types from data patterns

### Issue 2: High Null Rate (32% of tables)

**Why this happens:**
- Original tables are sparse
- Multi-row headers create confusion
- Page breaks split tables
- Footnotes included in extraction area

**Examples:**
```
SDS-31_Part1_table_008.csv:
  Null values: 35.1%
  Reason: Sparse temperature series data with many empty cells
```

### Issue 3: Low Overall Quality (28% of tables)

Tables with overall scores <60% typically have multiple issues:
- Poor headers (all tables)
- High null rate
- Small table size (<5 rows)
- Complex multi-level headers

---

## Improvement Recommendations

### Priority 1: Header Detection (Highest Impact)

**Current:** 0% accuracy
**Target:** 70%+ accuracy

**Approach 1: First-Row Header Detection**
```python
def detect_headers_from_first_row(df: pd.DataFrame) -> List[str]:
    """
    Check if first row contains text (not numbers) and use as headers.
    """
    first_row = df.iloc[0]
    if all(isinstance(v, str) and not v.replace('.', '').isdigit() for v in first_row):
        headers = first_row.tolist()
        return df[1:].set_axis(headers, axis=1)
    return df
```

**Approach 2: PDF Text Mining**
Extract text above table area to find header row:
```python
import pdfplumber

def extract_table_with_headers(pdf_path, page_num, table_bbox):
    """
    Extract text region above table to find headers.
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        # Extract region 20 pixels above table
        header_bbox = (table_bbox[0], table_bbox[1] - 20, table_bbox[2], table_bbox[1])
        header_text = page.crop(header_bbox).extract_text()
        # Parse header_text into column names
```

**Approach 3: Use Column Type Detection**
Leverage existing column detection to generate default headers:
```python
# Current: ['0', '1', '2', '3']
# Improved: ['Temperature (°C)', 'Mass %', 'Molality', 'Phase']
```

**Expected improvement:** +30-40% overall accuracy

### Priority 2: Multi-Page Table Handling

**Current:** Each page extracted independently
**Target:** Merge tables split across pages

**Approach:**
```python
def merge_split_tables(table1: pd.DataFrame, table2: pd.DataFrame) -> pd.DataFrame:
    """
    Detect if table2 is continuation of table1.
    """
    # Check if column structures match
    if table1.shape[1] == table2.shape[1]:
        # Check if table2 starts with continuation pattern
        if not has_header_row(table2):
            return pd.concat([table1, table2], ignore_index=True)
    return table2
```

**Expected improvement:** +5-10% data completeness

### Priority 3: Smart Null Handling

**Current:** Empty cells become `NaN`
**Target:** Distinguish between legitimate nulls and extraction errors

**Approach:**
```python
def validate_sparse_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check if high null rate is due to sparse data or extraction issues.
    """
    # If nulls follow pattern (e.g., every other row), likely legitimate
    # If random, might be extraction error
    if is_systematic_sparsity(df):
        return df  # Keep as-is
    else:
        # Try re-extraction with different parameters
        return retry_extraction(df)
```

**Expected improvement:** +3-5% data completeness

### Priority 4: Area-Based Extraction

**Current:** Auto-detect table boundaries
**Target:** Manual area specification for problematic tables

**Approach:**
```python
# For tables with known issues, use explicit coordinates
problem_tables = {
    'SDS-31_Part1_table_007': {
        'area': [100, 50, 700, 550],  # top, left, bottom, right
        'columns': [100, 150, 200, 250, 300, 350, 400, 450, 500, 550]
    }
}

tables = tabula.read_pdf(
    pdf_path,
    area=problem_tables[filename]['area'],
    columns=problem_tables[filename]['columns']
)
```

**Expected improvement:** +10-15% for specific problematic tables

### Priority 5: Post-Processing Validation

**Current:** Minimal validation
**Target:** Detect and flag extraction errors

**Approach:**
```python
def validate_extraction(df: pd.DataFrame, metadata: dict) -> dict:
    """
    Run quality checks and flag issues.
    """
    issues = []

    # Check 1: Unrealistic values
    if has_values_outside_expected_range(df):
        issues.append("Out-of-range values detected")

    # Check 2: Duplicate rows
    if df.duplicated().sum() > 0:
        issues.append(f"{df.duplicated().sum()} duplicate rows")

    # Check 3: Column count mismatch
    if df.shape[1] != metadata.get('expected_columns', df.shape[1]):
        issues.append("Column count mismatch")

    return {
        'quality_score': calculate_quality_score(df),
        'issues': issues,
        'needs_review': len(issues) > 0
    }
```

---

## Implementation Plan

### Phase 1: Header Detection (Week 1)
1. Implement first-row header detection
2. Update column type detection to generate default headers
3. Re-run extraction pipeline
4. **Expected result:** 70%+ header quality, 80%+ overall accuracy

### Phase 2: Validation & Flagging (Week 2)
1. Add post-extraction validation
2. Flag tables needing manual review
3. Create review interface for fixing problematic tables
4. **Expected result:** Identify 20-30 tables for manual correction

### Phase 3: Advanced Techniques (Week 3-4)
1. Implement multi-page table merging
2. Test area-based extraction for flagged tables
3. Develop PDF text mining for headers
4. **Expected result:** 85%+ overall accuracy

---

## Comparison with OCR Cleaning

Our **OCR cleaning script** (already implemented) has been highly effective:

**Results from 20 sample tables:**
- 205 comma decimal errors fixed (`,` → `.`)
- 1 phase column added
- 0 OCR artifacts in final output

**Effectiveness:** ~95% for numeric cleaning

The combination of OCR cleaning + column detection + phase extraction brings us from ~50% raw accuracy to current **63.6%** accuracy.

---

## Recommended Next Steps

1. **Immediate (This Week):**
   - Implement first-row header detection
   - Generate default headers from column types
   - Update web interface to display improved headers

2. **Short-term (Next 2 Weeks):**
   - Add extraction validation and flagging
   - Implement multi-page table merging
   - Manual review of 20-30 most problematic tables

3. **Long-term (Next Month):**
   - PDF text mining for header extraction
   - Area-based extraction for specific problematic tables
   - Semi-automated table correction workflow

4. **Stretch Goals:**
   - Train ML model for header detection
   - Implement table structure recognition
   - Build confidence scoring system

---

## Conclusion

**Current state:** 63.6% overall extraction accuracy

**Main bottleneck:** Header detection (0% accuracy)

**Quick win:** Implementing header detection could boost accuracy to 80%+ with moderate effort

**Long-term potential:** 90%+ accuracy with advanced techniques and manual review

The extraction pipeline is functional and producing usable data, but header improvements would significantly enhance data usability and searchability.
