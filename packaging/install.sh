#!/usr/bin/env bash
# Linux Installation Script for SQRT_Gem
# Satisfies Requirements: Sections 8, 9 of TZ_1.md

set -e

INSTALL_DIR="${HOME}/.local/share/sqrt_gem"
BIN_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${HOME}/.local/share/applications"

echo "=== Installing SQRT_Gem ==="
mkdir -p "${INSTALL_DIR}"
mkdir -p "${BIN_DIR}"
mkdir -p "${DESKTOP_DIR}"

# Copy application files
cp -r src locales "${INSTALL_DIR}/"
cat << 'EOF' > "${INSTALL_DIR}/sqrt_gem"
#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}"
python3 "${SCRIPT_DIR}/src/main.py" "$@"
EOF
chmod +x "${INSTALL_DIR}/sqrt_gem"

# Symlink to bin
ln -sf "${INSTALL_DIR}/sqrt_gem" "${BIN_DIR}/sqrt_gem"

# Desktop launcher
cat << EOF > "${DESKTOP_DIR}/sqrt_gem.desktop"
[Desktop Entry]
Name=SQRT_Gem Calculator
Comment=High-Precision Analytical Math Calculator
Exec=${BIN_DIR}/sqrt_gem
Terminal=false
Type=Application
Categories=Utility;Calculator;Science;Math;
EOF

echo "Installation complete! You can run 'sqrt_gem' from terminal or launch from Applications menu."
