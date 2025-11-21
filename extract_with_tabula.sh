#!/bin/bash
################################################################################
# Automated Solubility Data Extraction using Tabula-Java
################################################################################
# This script uses the official tabula-java command-line tool to extract
# tables from SDS-31 PDF files automatically.
#
# Prerequisites:
#   1. Java 8 or higher: java -version
#   2. Tabula JAR file (auto-downloaded by this script)
#
# Usage:
#   ./extract_with_tabula.sh [pdf_file] [pages] [output_dir]
#
# Examples:
#   ./extract_with_tabula.sh Data/SDS-31_Part7.pdf "10-30" extracted_data
#   ./extract_with_tabula.sh Data/SDS-31_Part7.pdf "all" extracted_data
################################################################################

set -e  # Exit on error

# Configuration
TABULA_VERSION="1.0.5"
TABULA_JAR="tabula-${TABULA_VERSION}-jar-with-dependencies.jar"
TABULA_URL="https://github.com/tabulapdf/tabula-java/releases/download/v${TABULA_VERSION}/${TABULA_JAR}"
DATA_DIR="Data"
DEFAULT_OUTPUT_DIR="extracted_data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

################################################################################
# Functions
################################################################################

print_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Solubility Data Extraction - Tabula-Java Automation    ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

check_java() {
    echo -n "Checking Java installation... "
    if command -v java &> /dev/null; then
        JAVA_VERSION=$(java -version 2>&1 | awk -F '"' '/version/ {print $2}' | cut -d'.' -f1)
        if [ "$JAVA_VERSION" -ge 8 ]; then
            print_success "Java found (version $(java -version 2>&1 | awk -F '"' '/version/ {print $2}'))"
            return 0
        else
            print_error "Java version too old (need 8+)"
            return 1
        fi
    else
        print_error "Java not found"
        echo
        echo "Please install Java:"
        echo "  Ubuntu/Debian: sudo apt-get install default-jre"
        echo "  macOS: brew install openjdk"
        echo "  Windows: https://www.java.com/download/"
        return 1
    fi
}

download_tabula() {
    if [ -f "$TABULA_JAR" ]; then
        print_success "Tabula JAR already exists: $TABULA_JAR"
        return 0
    fi

    echo
    print_info "Downloading Tabula-Java v${TABULA_VERSION}..."
    print_info "URL: $TABULA_URL"

    if command -v wget &> /dev/null; then
        wget -q --show-progress "$TABULA_URL" -O "$TABULA_JAR"
    elif command -v curl &> /dev/null; then
        curl -L --progress-bar "$TABULA_URL" -o "$TABULA_JAR"
    else
        print_error "Neither wget nor curl found"
        echo "Please download manually from:"
        echo "  $TABULA_URL"
        return 1
    fi

    if [ -f "$TABULA_JAR" ]; then
        print_success "Downloaded: $TABULA_JAR ($(du -h "$TABULA_JAR" | cut -f1))"
        return 0
    else
        print_error "Download failed"
        return 1
    fi
}

extract_tables() {
    local pdf_file="$1"
    local pages="$2"
    local output_dir="$3"
    local pdf_basename=$(basename "$pdf_file" .pdf)

    print_info "Processing: $pdf_file"
    print_info "Pages: $pages"
    print_info "Output directory: $output_dir"
    echo

    # Create output directory
    mkdir -p "$output_dir"

    # Extract with lattice mode (for bordered tables)
    local output_lattice="${output_dir}/${pdf_basename}_lattice_p${pages}.csv"
    echo -n "Extracting with lattice mode (bordered tables)... "

    if java -jar "$TABULA_JAR" \
        --pages "$pages" \
        --lattice \
        --format CSV \
        --outfile "$output_lattice" \
        "$pdf_file" 2>/dev/null; then

        if [ -s "$output_lattice" ]; then
            print_success "Success: $output_lattice"
        else
            print_warning "No tables found (lattice mode)"
            rm -f "$output_lattice"
        fi
    else
        print_error "Failed (lattice mode)"
    fi

    # Extract with stream mode (for borderless tables)
    local output_stream="${output_dir}/${pdf_basename}_stream_p${pages}.csv"
    echo -n "Extracting with stream mode (borderless tables)... "

    if java -jar "$TABULA_JAR" \
        --pages "$pages" \
        --stream \
        --format CSV \
        --outfile "$output_stream" \
        "$pdf_file" 2>/dev/null; then

        if [ -s "$output_stream" ]; then
            print_success "Success: $output_stream"
        else
            print_warning "No tables found (stream mode)"
            rm -f "$output_stream"
        fi
    else
        print_error "Failed (stream mode)"
    fi

    # Also try without mode specification (auto-detect)
    local output_auto="${output_dir}/${pdf_basename}_auto_p${pages}.csv"
    echo -n "Extracting with auto-detect mode... "

    if java -jar "$TABULA_JAR" \
        --pages "$pages" \
        --format CSV \
        --outfile "$output_auto" \
        "$pdf_file" 2>/dev/null; then

        if [ -s "$output_auto" ]; then
            print_success "Success: $output_auto"
        else
            print_warning "No tables found (auto mode)"
            rm -f "$output_auto"
        fi
    else
        print_error "Failed (auto mode)"
    fi

    echo
    print_info "Extraction complete! Check the $output_dir directory"
}

batch_extract_all() {
    local pages="$1"
    local output_dir="$2"

    print_info "Batch processing all PDF files in $DATA_DIR/"
    echo

    if [ ! -d "$DATA_DIR" ]; then
        print_error "Directory not found: $DATA_DIR"
        return 1
    fi

    local pdf_count=0
    for pdf_file in "$DATA_DIR"/*.pdf; do
        if [ -f "$pdf_file" ]; then
            ((pdf_count++))
            echo -e "${BLUE}────────────────────────────────────────────────────────${NC}"
            extract_tables "$pdf_file" "$pages" "$output_dir"
        fi
    done

    if [ $pdf_count -eq 0 ]; then
        print_error "No PDF files found in $DATA_DIR/"
        return 1
    fi

    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
    print_success "Processed $pdf_count PDF file(s)"
}

show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] [PDF_FILE] [PAGES] [OUTPUT_DIR]

OPTIONS:
    --all           Process all PDFs in Data/ directory
    --help          Show this help message

ARGUMENTS:
    PDF_FILE        Path to PDF file (default: Data/SDS-31_Part7.pdf)
    PAGES           Page range to extract (default: 10-30)
                    Examples: "all", "10-30", "1-10,20-30"
    OUTPUT_DIR      Output directory (default: extracted_data)

EXAMPLES:
    # Extract pages 10-30 from Part 7
    $0

    # Extract all pages from Part 7
    $0 Data/SDS-31_Part7.pdf all

    # Extract specific pages from Part 1
    $0 Data/SDS-31_Part1.pdf "15-25" my_output

    # Process all PDF files
    $0 --all

    # Process all PDFs, pages 20-50
    $0 --all 20-50

NOTES:
    - First run will download tabula-java JAR file (~65MB)
    - Java 8+ must be installed
    - Extracts with three modes: lattice, stream, and auto-detect
    - Output is in CSV format
    - Empty results are automatically removed

EOF
}

################################################################################
# Main Script
################################################################################

main() {
    print_header

    # Parse arguments
    if [ "$1" == "--help" ]; then
        show_usage
        exit 0
    fi

    # Check Java
    if ! check_java; then
        exit 1
    fi

    # Download Tabula if needed
    if ! download_tabula; then
        exit 1
    fi

    echo
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
    echo

    # Handle batch mode
    if [ "$1" == "--all" ]; then
        local pages="${2:-10-30}"
        local output_dir="${3:-$DEFAULT_OUTPUT_DIR}"
        batch_extract_all "$pages" "$output_dir"
    else
        # Single file mode
        local pdf_file="${1:-Data/SDS-31_Part7.pdf}"
        local pages="${2:-10-30}"
        local output_dir="${3:-$DEFAULT_OUTPUT_DIR}"

        if [ ! -f "$pdf_file" ]; then
            print_error "PDF file not found: $pdf_file"
            exit 1
        fi

        extract_tables "$pdf_file" "$pages" "$output_dir"
    fi

    # Summary
    echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
    echo
    print_success "Done!"
    echo
    echo "Next steps:"
    echo "  1. Check the extracted CSV files in the output directory"
    echo "  2. Compare lattice vs stream vs auto results"
    echo "  3. Use the best-performing mode for your tables"
    echo "  4. Process remaining PDFs with: $0 --all"
    echo
}

# Run main function
main "$@"
