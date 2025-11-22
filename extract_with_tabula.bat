@echo off
REM ############################################################################
REM Automated Solubility Data Extraction using Tabula-Java (Windows)
REM ############################################################################
REM
REM Prerequisites:
REM   1. Java 8 or higher installed
REM   2. Tabula JAR file (auto-downloaded by this script)
REM
REM Usage:
REM   extract_with_tabula.bat [pdf_file] [pages]
REM
REM Examples:
REM   extract_with_tabula.bat Data\SDS-31_Part7.pdf 10-30
REM   extract_with_tabula.bat Data\SDS-31_Part7.pdf all
REM ############################################################################

setlocal enabledelayedexpansion

REM Configuration
set TABULA_VERSION=1.0.5
set TABULA_JAR=tabula-%TABULA_VERSION%-jar-with-dependencies.jar
set TABULA_URL=https://github.com/tabulapdf/tabula-java/releases/download/v%TABULA_VERSION%/%TABULA_JAR%
set DATA_DIR=Data
set OUTPUT_DIR=extracted_data

REM Parse arguments
set PDF_FILE=%1
set PAGES=%2

if "%PDF_FILE%"=="" set PDF_FILE=Data\SDS-31_Part7.pdf
if "%PAGES%"=="" set PAGES=10-30

echo.
echo ========================================================================
echo   Solubility Data Extraction - Tabula-Java Automation (Windows)
echo ========================================================================
echo.

REM Check Java
echo Checking Java installation...
java -version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Java not found!
    echo.
    echo Please install Java from: https://www.java.com/download/
    echo.
    pause
    exit /b 1
)
echo [OK] Java found
echo.

REM Download Tabula if needed
if not exist "%TABULA_JAR%" (
    echo Downloading Tabula-Java v%TABULA_VERSION%...
    echo URL: %TABULA_URL%
    echo.

    REM Try to download using PowerShell
    powershell -Command "& {Invoke-WebRequest -Uri '%TABULA_URL%' -OutFile '%TABULA_JAR%'}"

    if errorlevel 1 (
        echo [ERROR] Download failed!
        echo.
        echo Please download manually from:
        echo   %TABULA_URL%
        echo.
        pause
        exit /b 1
    )
    echo [OK] Downloaded: %TABULA_JAR%
) else (
    echo [OK] Tabula JAR found: %TABULA_JAR%
)
echo.

REM Check if PDF exists
if not exist "%PDF_FILE%" (
    echo [ERROR] PDF file not found: %PDF_FILE%
    echo.
    pause
    exit /b 1
)

REM Create output directory
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Get filename without extension
for %%F in ("%PDF_FILE%") do set PDF_BASENAME=%%~nF

echo ========================================================================
echo Processing: %PDF_FILE%
echo Pages: %PAGES%
echo Output directory: %OUTPUT_DIR%
echo ========================================================================
echo.

REM Extract with lattice mode
set OUTPUT_LATTICE=%OUTPUT_DIR%\%PDF_BASENAME%_lattice_p%PAGES%.csv
echo Extracting with lattice mode (bordered tables)...
java -jar "%TABULA_JAR%" --pages %PAGES% --lattice --format CSV --outfile "%OUTPUT_LATTICE%" "%PDF_FILE%" >nul 2>&1
if exist "%OUTPUT_LATTICE%" (
    echo [OK] Success: %OUTPUT_LATTICE%
) else (
    echo [WARN] No tables found with lattice mode
)

REM Extract with stream mode
set OUTPUT_STREAM=%OUTPUT_DIR%\%PDF_BASENAME%_stream_p%PAGES%.csv
echo Extracting with stream mode (borderless tables)...
java -jar "%TABULA_JAR%" --pages %PAGES% --stream --format CSV --outfile "%OUTPUT_STREAM%" "%PDF_FILE%" >nul 2>&1
if exist "%OUTPUT_STREAM%" (
    echo [OK] Success: %OUTPUT_STREAM%
) else (
    echo [WARN] No tables found with stream mode
)

REM Extract with auto-detect
set OUTPUT_AUTO=%OUTPUT_DIR%\%PDF_BASENAME%_auto_p%PAGES%.csv
echo Extracting with auto-detect mode...
java -jar "%TABULA_JAR%" --pages %PAGES% --format CSV --outfile "%OUTPUT_AUTO%" "%PDF_FILE%" >nul 2>&1
if exist "%OUTPUT_AUTO%" (
    echo [OK] Success: %OUTPUT_AUTO%
) else (
    echo [WARN] No tables found with auto mode
)

echo.
echo ========================================================================
echo Extraction complete!
echo ========================================================================
echo.
echo Check the %OUTPUT_DIR% directory for your CSV files.
echo.
echo Next steps:
echo   1. Review the extracted CSV files
echo   2. Compare lattice vs stream vs auto results
echo   3. Use the best mode for your tables
echo.
pause
