#!/usr/bin/env bash
# Debian Package (.deb) Builder using standard dpkg-deb

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_ROOT}"

echo "=== Building Debian Package (.deb) for SQRT_Gem ==="

DEB_ROOT="${PROJECT_ROOT}/build_deb_temp"
rm -rf "${DEB_ROOT}"
mkdir -p "${DEB_ROOT}"

# Copy package structure
cp -r "${PROJECT_ROOT}/packaging/deb/"* "${DEB_ROOT}/"

# Prepare payload in /opt/sqrt-gem
mkdir -p "${DEB_ROOT}/opt/sqrt-gem"
if [ -d "${PROJECT_ROOT}/dist/SQRT_Gem" ]; then
    echo "Using PyInstaller binaries from dist/SQRT_Gem..."
    cp -r "${PROJECT_ROOT}/dist/SQRT_Gem/"* "${DEB_ROOT}/opt/sqrt-gem/"
else
    echo "dist/SQRT_Gem not found; packaging Python source files..."
    cp -r "${PROJECT_ROOT}/src" "${DEB_ROOT}/opt/sqrt-gem/"
    cp -r "${PROJECT_ROOT}/locales" "${DEB_ROOT}/opt/sqrt-gem/"
    cp "${PROJECT_ROOT}/requirements.txt" "${DEB_ROOT}/opt/sqrt-gem/"
fi

# Ensure correct permissions
find "${DEB_ROOT}" -type d -exec chmod 755 {} +
chmod 755 "${DEB_ROOT}/DEBIAN/postinst" "${DEB_ROOT}/DEBIAN/postrm" "${DEB_ROOT}/usr/bin/sqrt-gem"

mkdir -p "${PROJECT_ROOT}/dist_installer"
OUTPUT_DEB="${PROJECT_ROOT}/dist_installer/sqrt-gem_1.0.0_amd64.deb"

dpkg-deb --build --root-owner-group "${DEB_ROOT}" "${OUTPUT_DEB}"
rm -rf "${DEB_ROOT}"

echo "=== Debian Package Successfully Created: ${OUTPUT_DEB} ==="
