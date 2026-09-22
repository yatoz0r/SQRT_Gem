@echo off
setlocal enabledelayedexpansion
echo =======================================================
echo  SQRT_Gem Windows Installer (MSI) Builder
echo =======================================================

cd /d "%~dp0\.."

if not exist "dist\SQRT_Gem\SQRT_Gem.exe" (
    echo [INFO] dist\SQRT_Gem\SQRT_Gem.exe not found. Building executable first...
    call packaging\build_windows.bat
    if errorlevel 1 (
        echo [ERROR] Failed to build executable with PyInstaller.
        exit /b 1
    )
)

if not exist "packaging\icon.ico" (
    echo [INFO] packaging\icon.ico missing. Generating default icon...
    python -c "
import struct
ico_header = struct.pack('<HHH', 0, 1, 1)
ico_entry = struct.pack('<BBBBHHII', 16, 16, 0, 0, 1, 32, 40 + 16*16*4, 22)
bmi = struct.pack('<IIIHHIIIIII', 40, 16, 32, 1, 32, 0, 16*16*4, 0, 0, 0, 0)
pixel_data = b'\x4A\x90\xE2\xFF' * (16 * 16)
mask = b'\x00' * (16 * 2)
with open('packaging/icon.ico', 'wb') as f:
    f.write(ico_header + ico_entry + bmi + pixel_data + mask)
"
)

if not exist "dist_installer" mkdir "dist_installer"

set WIX_BIN=
if exist "%WIX%\bin\candle.exe" set WIX_BIN=%WIX%\bin
if exist "C:\Program Files (x86)\WiX Toolset v3.11\bin\candle.exe" set WIX_BIN=C:\Program Files (x86)\WiX Toolset v3.11\bin
if exist "C:\Program Files\WiX Toolset v3.11\bin\candle.exe" set WIX_BIN=C:\Program Files\WiX Toolset v3.11\bin

where candle.exe >nul 2>nul
if %errorlevel% equ 0 (
    set WIX_CANDLE=candle.exe
    set WIX_LIGHT=light.exe
) else if defined WIX_BIN (
    set WIX_CANDLE="%WIX_BIN%\candle.exe"
    set WIX_LIGHT="%WIX_BIN%\light.exe"
) else (
    where wix.exe >nul 2>nul
    if %errorlevel% equ 0 (
        echo [INFO] Building MSI using WiX v4 CLI...
        wix build packaging\product.wxs -o dist_installer\SQRT_Gem.msi
        if %errorlevel% equ 0 (
            echo [SUCCESS] MSI built: dist_installer\SQRT_Gem.msi
            exit /b 0
        )
    )
    echo [ERROR] WiX Toolset not found in PATH or standard Program Files locations!
    echo Please install WiX Toolset v3.11: https://wixtoolset.org/releases/
    echo Or install via winget: winget install WiX.Toolset
    exit /b 1
)

echo [INFO] Compiling WiX manifest (candle)...
%WIX_CANDLE% -nologo packaging\product.wxs -out dist_installer\product.wixobj
if %errorlevel% neq 0 exit /b %errorlevel%

echo [INFO] Linking MSI installer (light)...
%WIX_LIGHT% -nologo -ext WixUIExtension dist_installer\product.wixobj -out dist_installer\SQRT_Gem.msi
if %errorlevel% neq 0 exit /b %errorlevel%

del dist_installer\product.wixobj 2>nul
del dist_installer\SQRT_Gem.wixpdb 2>nul

echo =======================================================
echo [SUCCESS] MSI Package created: dist_installer\SQRT_Gem.msi
echo Silent install command: msiexec /i dist_installer\SQRT_Gem.msi /passive /norestart
echo =======================================================
