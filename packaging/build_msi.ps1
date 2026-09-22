# PowerShell MSI build script for SQRT_Gem using WiX Toolset
[CmdletBinding()]
param(
    [string]$Version = "1.0.0",
    [string]$OutputDir = "dist_installer"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
Set-Location $ProjectRoot

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host " SQRT_Gem MSI Installer Builder (PowerShell)" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

$ExePath = Join-Path $ProjectRoot "dist\SQRT_Gem\SQRT_Gem.exe"
if (-not (Test-Path $ExePath)) {
    Write-Host "[INFO] Executable not found. Compiling with PyInstaller..." -ForegroundColor Yellow
    & "$ProjectRoot\packaging\build_windows.bat"
}

$IconPath = Join-Path $ProjectRoot "packaging\icon.ico"
if (-not (Test-Path $IconPath)) {
    Write-Host "[INFO] Generating default packaging\icon.ico..." -ForegroundColor Yellow
    python -c @"
import struct
ico_header = struct.pack('<HHH', 0, 1, 1)
ico_entry = struct.pack('<BBBBHHII', 16, 16, 0, 0, 1, 32, 40 + 16*16*4, 22)
bmi = struct.pack('<IIIHHIIIIII', 40, 16, 32, 1, 32, 0, 16*16*4, 0, 0, 0, 0)
pixel_data = b'\x4A\x90\xE2\xFF' * (16 * 16)
mask = b'\x00' * (16 * 2)
with open('packaging/icon.ico', 'wb') as f:
    f.write(ico_header + ico_entry + bmi + pixel_data + mask)
"@
}

$OutDirFull = Join-Path $ProjectRoot $OutputDir
if (-not (Test-Path $OutDirFull)) {
    New-Item -ItemType Directory -Path $OutDirFull -Force | Out-Null
}

$Candle = Get-Command "candle.exe" -ErrorAction SilentlyContinue
$Light = Get-Command "light.exe" -ErrorAction SilentlyContinue

if (-not $Candle) {
    $WixPaths = @(
        "$env:WIX\bin",
        "${env:ProgramFiles(x86)}\WiX Toolset v3.11\bin",
        "$env:ProgramFiles\WiX Toolset v3.11\bin"
    )
    foreach ($p in $WixPaths) {
        if (Test-Path (Join-Path $p "candle.exe")) {
            $CandlePath = Join-Path $p "candle.exe"
            $LightPath = Join-Path $p "light.exe"
            break
        }
    }
} else {
    $CandlePath = $Candle.Source
    $LightPath = $Light.Source
}

$MsiOutput = Join-Path $OutDirFull "SQRT_Gem.msi"

if ($CandlePath -and (Test-Path $CandlePath)) {
    Write-Host "[INFO] Using WiX v3 compiler: $CandlePath" -ForegroundColor Green
    $WixObj = Join-Path $OutDirFull "product.wixobj"
    & $CandlePath -nologo "$ProjectRoot\packaging\product.wxs" -out $WixObj
    & $LightPath -nologo $WixObj -out $MsiOutput
    Remove-Item $WixObj -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $OutDirFull "SQRT_Gem.wixpdb") -ErrorAction SilentlyContinue
} else {
    $WixCli = Get-Command "wix.exe" -ErrorAction SilentlyContinue
    if ($WixCli) {
        Write-Host "[INFO] Using WiX v4 CLI..." -ForegroundColor Green
        & wix build "$ProjectRoot\packaging\product.wxs" -o $MsiOutput
    } else {
        Write-Error "WiX Toolset not detected. Please install WiX Toolset v3.11 or v4."
        exit 1
    }
}

Write-Host "=======================================================" -ForegroundColor Green
Write-Host "[SUCCESS] MSI successfully generated: $MsiOutput" -ForegroundColor Green
Write-Host "Silent installation: msiexec /i `"$MsiOutput`" /passive /norestart" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Green
