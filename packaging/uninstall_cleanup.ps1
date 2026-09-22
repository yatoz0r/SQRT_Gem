# PowerShell uninstallation cleanup script for SQRT_Gem
# Satisfies Section 10 of TZ_1.md (Clean uninstallation with user data policy choice)

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$Silent
)

$ErrorActionPreference = "SilentlyContinue"

$DataDir = Join-Path $env:APPDATA "SQRT_Gem"
if (-not (Test-Path $DataDir)) {
    exit 0
}

if ($Force) {
    Remove-Item -Recurse -Force $DataDir -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "HKCU:\Software\SQRT_Gem" -ErrorAction SilentlyContinue
    exit 0
}

# If interactive, prompt user for deletion of user data
try {
    Add-Type -AssemblyName System.Windows.Forms
    
    $promptMsg = "Удалить также пользовательские данные приложения SQRT_Gem (историю вычислений и настройки)?`n`n" +
                 "• Да (Yes) — полностью удалить все данные (%APPDATA%\SQRT_Gem)`n" +
                 "• Нет (No) — сохранить историю вычислений и настройки для будущих версий`n`n" +
                 "Do you also want to delete user data (calculation history and settings)?"

    $result = [System.Windows.Forms.MessageBox]::Show(
        $promptMsg,
        "SQRT_Gem Calculator — Удаление программы",
        [System.Windows.Forms.MessageBoxButtons]::YesNo,
        [System.Windows.Forms.MessageBoxIcon]::Question
    )

    if ($result -eq [System.Windows.Forms.DialogResult]::Yes) {
        Remove-Item -Recurse -Force $DataDir -ErrorAction SilentlyContinue
        Remove-Item -Recurse -Force "HKCU:\Software\SQRT_Gem" -ErrorAction SilentlyContinue
    }
} catch {
    # If UI cannot be shown (e.g. non-interactive service), do not crash uninstaller
    if ($Silent) {
        Remove-Item -Recurse -Force $DataDir -ErrorAction SilentlyContinue
    }
}

exit 0
