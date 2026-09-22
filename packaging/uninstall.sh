#!/usr/bin/env bash
# Linux Uninstallation Script for SQRT_Gem
# Satisfies Requirements: Section 10 of TZ_1.md (Clean uninstall with choice to keep/delete user data)

set -e

INSTALL_DIR="${HOME}/.local/share/sqrt_gem"
BIN_FILE="${HOME}/.local/bin/sqrt_gem"
DESKTOP_FILE="${HOME}/.local/share/applications/sqrt_gem.desktop"
DATA_DIR="${HOME}/.config/sqrt_gem"

echo "=== Uninstalling SQRT_Gem ==="

# Remove application files and shortcuts
rm -rf "${INSTALL_DIR}"
rm -f "${BIN_FILE}"
rm -f "${DESKTOP_FILE}"

echo "Application binaries and shortcuts successfully removed."

# Handle user data
if [ "$1" == "--purge" ]; then
    echo "Purging user data..."
    rm -rf "${DATA_DIR}"
    echo "All user data deleted."
else
    read -p "Do you want to delete user calculation history and settings (${DATA_DIR})? [y/N]: " choice
    case "$choice" in 
      y|Y ) 
        rm -rf "${DATA_DIR}"
        echo "User data deleted."
        ;;
      * ) 
        echo "User data preserved in ${DATA_DIR}."
        ;;
    esac
fi

echo "Uninstallation finished."
