@echo off
REM PyInstaller build script for Windows x64
REM Satisfies Section 18 of TZ_1.md

echo === Building SQRT_Gem for Windows ===
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onedir --windowed ^
    --name "SQRT_Gem" ^
    --add-data "locales;locales" ^
    src/main.py

echo Build complete. Output located in dist/SQRT_Gem/
