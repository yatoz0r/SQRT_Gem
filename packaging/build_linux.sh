#!/usr/bin/env bash
# PyInstaller build script for Linux x64
# Satisfies Section 18 of TZ_1.md

set -e

echo "=== Building SQRT_Gem for Linux ==="
python3 -m pip install pyinstaller
python3 -m PyInstaller --noconfirm --onedir --windowed \
    --name "SQRT_Gem" \
    --add-data "locales:locales" \
    src/main.py

echo "Build complete. Output located in dist/SQRT_Gem/"
