@echo off
REM ========================================
REM SummaryForDoc - PyInstaller Build Script
REM ========================================
echo.
echo [1/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [2/4] Building with PyInstaller...
python -m PyInstaller SummaryForDoc.spec
if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo [3/4] Copying Tesseract files...
set TESSERACT_PATH=C:\Program Files\Tesseract-OCR
set BUILD_DIR=dist\SummaryForDoc

REM Create tesseract directories
mkdir "%BUILD_DIR%\tesseract\tessdata" 2>nul

REM Copy Tesseract executable
copy "%TESSERACT_PATH%\tesseract.exe" "%BUILD_DIR%\tesseract\" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy tesseract.exe
    echo Please verify Tesseract is installed at: %TESSERACT_PATH%
    pause
    exit /b 1
)

REM Copy language data
copy "%TESSERACT_PATH%\tessdata\eng.traineddata" "%BUILD_DIR%\tesseract\tessdata\" >nul
copy "%TESSERACT_PATH%\tessdata\jpn.traineddata" "%BUILD_DIR%\tesseract\tessdata\" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy Japanese language data
    echo See: TESSERACT_JAPANESE_INSTALL.md
    pause
    exit /b 1
)

REM Copy all DLL files
copy "%TESSERACT_PATH%\*.dll" "%BUILD_DIR%\tesseract\" >nul

echo.
echo [4/4] Verifying build...
if not exist "%BUILD_DIR%\SummaryForDoc.exe" (
    echo ERROR: SummaryForDoc.exe not found
    pause
    exit /b 1
)

if not exist "%BUILD_DIR%\tesseract\tesseract.exe" (
    echo ERROR: tesseract.exe not found
    pause
    exit /b 1
)

if not exist "%BUILD_DIR%\tesseract\tessdata\jpn.traineddata" (
    echo ERROR: jpn.traineddata not found
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Location: %BUILD_DIR%
echo.
echo To run the application:
echo   cd dist\SummaryForDoc
echo   SummaryForDoc.exe
echo.
pause
