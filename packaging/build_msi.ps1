# PowerShell MSI build script for SQRT_Gem using WiX Toolset
[CmdletBinding()]
param(
    [string]$Version = "1.0.0",
    [string]$OutputDir = "dist_installer"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
Set-Location $ProjectRoot

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
Set-Location $ProjectRoot

python "$PSScriptRoot\build_msi.py"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

