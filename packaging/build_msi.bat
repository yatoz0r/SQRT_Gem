@echo off
setlocal enabledelayedexpansion
echo =======================================================
echo  SQRT_Gem Windows Installer (MSI) Builder
echo =======================================================

cd /d "%~dp0\.."

python "%~dp0build_msi.py"
if %errorlevel% neq 0 exit /b %errorlevel%

