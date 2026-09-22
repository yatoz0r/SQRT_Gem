#!/usr/bin/env python3
"""WiX MSI Installer Generator and Builder for SQRT_Gem.

Scans the PyInstaller output directory (dist/SQRT_Gem) and automatically generates
a complete, robust, 64-bit WiX XML manifest (product.wxs) including all runtime
dependencies (_internal, PySide6 DLLs, Qt plugins, assets).
Then compiles it into a production-grade .msi installer using WiX Toolset.
"""

import os
import sys
import uuid
import hashlib
import shutil
import subprocess
from pathlib import Path

NAMESPACE_UUID = uuid.UUID("c8e28b91-4475-4c3d-8692-7e1a63dc458f")


def sanitize_id(prefix: str, rel_path: str) -> str:
    """Create a valid, deterministic WiX identifier (letters, digits, underscores, <= 72 chars)."""
    norm = rel_path.replace("\\", "/").strip("/")
    h = hashlib.md5(norm.encode("utf-8")).hexdigest()[:12]
    clean_name = "".join(c if c.isalnum() else "_" for c in Path(norm).name)[:30]
    return f"{prefix}_{clean_name}_{h}"


def get_guid(rel_path: str) -> str:
    """Deterministic GUID from relative path."""
    return "{" + str(uuid.uuid5(NAMESPACE_UUID, rel_path.replace("\\", "/"))).upper() + "}"


def find_wix_tools():
    """Find candle.exe and light.exe."""
    candle = shutil.which("candle.exe")
    light = shutil.which("light.exe")
    if candle and light:
        return Path(candle), Path(light)

    search_dirs = [
        Path(r"C:\wix"),
        Path(r"C:\tools\wix"),
        Path(os.environ.get("WIX", "")) / "bin",
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "WiX Toolset v3.11" / "bin",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "WiX Toolset v3.11" / "bin",
    ]
    for d in search_dirs:
        c = d / "candle.exe"
        l = d / "light.exe"
        if c.exists() and l.exists():
            return c, l

    return None, None


def build_directory_tree(dist_dir: Path):
    """Build nested directory and file structure from dist_dir."""
    tree = {"dirs": {}, "files": []}
    for root, dirs, files in os.walk(dist_dir):
        rel_root = Path(root).relative_to(dist_dir)
        parts = rel_root.parts

        curr = tree
        for part in parts:
            if part not in curr["dirs"]:
                curr["dirs"][part] = {"dirs": {}, "files": []}
            curr = curr["dirs"][part]

        for f in files:
            curr["files"].append((f, Path(root) / f))
    return tree


def render_dir_xml(node, rel_path_parts, project_root: Path, indent_level=5):
    """Recursively generate WiX Directory and Component XML."""
    indent = "  " * indent_level
    lines = []
    component_ids = []

    # Render files in this directory
    rel_dir_str = "/".join(rel_path_parts)
    for fname, full_path in node["files"]:
        rel_file = f"{rel_dir_str}/{fname}" if rel_dir_str else fname
        cmp_id = sanitize_id("cmp", rel_file)
        fil_id = sanitize_id("fil", rel_file)
        guid = get_guid(rel_file)

        # Skip main executable here, handled with shortcuts
        if rel_file == "SQRT_Gem.exe":
            continue

        try:
            rel_src = full_path.relative_to(project_root)
            src_path = str(rel_src).replace("/", "\\")
        except Exception:
            src_path = str(full_path).replace("/", "\\")
        lines.append(f'{indent}<Component Id="{cmp_id}" Guid="{guid}" Win64="yes">')
        lines.append(f'{indent}  <File Id="{fil_id}" Source="{src_path}" KeyPath="yes" />')
        lines.append(f'{indent}</Component>')

        component_ids.append(cmp_id)

    # Render subdirectories
    for dname, child_node in sorted(node["dirs"].items()):
        dir_id = sanitize_id("dir", "/".join(rel_path_parts + [dname]))
        lines.append(f'{indent}<Directory Id="{dir_id}" Name="{dname}">')
        child_lines, child_cmps = render_dir_xml(child_node, rel_path_parts + [dname], project_root, indent_level + 1)
        lines.extend(child_lines)
        component_ids.extend(child_cmps)
        lines.append(f'{indent}</Directory>')

    return lines, component_ids


def generate_wxs(project_root: Path, dist_dir: Path, output_wxs: Path) -> list:
    """Generate product.wxs referencing all files in dist/SQRT_Gem."""
    tree = build_directory_tree(dist_dir)
    dir_xml_lines, component_ids = render_dir_xml(tree, [], project_root, indent_level=5)


    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">',
        '  <Product Id="*"',
        '           Name="SQRT_Gem High-Precision Calculator"',
        '           Language="1033"',
        '           Version="1.0.0"',
        '           Manufacturer="SQRT_Gem Team"',
        '           UpgradeCode="C8E28B91-4475-4C3D-8692-7E1A63DC458F">',
        '',
        '    <Package Id="*"',
        '             InstallerVersion="301"',
        '             Compressed="yes"',
        '             InstallScope="perMachine"',
        '             Platform="x64"',
        '             Description="SQRT_Gem High-Precision Analytical Math Calculator"',
        '             Comments="Precision calculator supporting arbitrary precision (1000+ digits)" />',
        '',
        '    <MajorUpgrade DowngradeErrorMessage="A newer version of SQRT_Gem is already installed."',
        '                  AllowSameVersionUpgrades="yes" />',
        '',
        '    <MediaTemplate EmbedCab="yes" />',
        '',
        '    <Icon Id="AppIcon.ico" SourceFile="packaging\\icon.ico" />',
        '    <Property Id="ARPPRODUCTICON" Value="AppIcon.ico" />',
        '    <Property Id="ARPHELPLINK" Value="https://github.com/yatoz0r/SQRT_Gem" />',
        '    <Property Id="ARPURLINFOABOUT" Value="https://github.com/yatoz0r/SQRT_Gem" />',
        '',
        '    <!-- Directory Hierarchy -->',
        '    <Directory Id="TARGETDIR" Name="SourceDir">',
        '      <Directory Id="ProgramFiles64Folder">',
        '        <Directory Id="INSTALLDIR" Name="SQRT_Gem">',
    ]

    # Insert generated files and directories
    xml_lines.extend(dir_xml_lines)

    # Main Executable, License & Uninstall Cleanup Script
    xml_lines.extend([
        '          <Component Id="MainExecutableCmp" Guid="{3E46C374-4C21-4E65-B5E3-72C59CE90C45}" Win64="yes">',
        '            <File Id="fil_SQRT_Gem_exe" Source="dist\\SQRT_Gem\\SQRT_Gem.exe" KeyPath="yes" />',
        '          </Component>',
        '          <Component Id="LicenseCmp" Guid="{8C9FD1A0-7176-4F15-896B-06381C43F623}" Win64="yes">',
        '            <File Id="fil_License" Source="LICENSE" KeyPath="yes" />',
        '          </Component>',
        '          <Component Id="UninstallCleanupCmp" Guid="{A1B2C3D4-E5F6-4A7B-8C9D-0E1F2A3B4C5D}" Win64="yes">',
        '            <File Id="fil_UninstallCleanup" Source="packaging\\uninstall_cleanup.ps1" KeyPath="yes" />',
        '          </Component>',
        '        </Directory>',
        '      </Directory>',
        '',
        '      <!-- Start Menu -->',
        '      <Directory Id="ProgramMenuFolder">',
        '        <Directory Id="ApplicationProgramsFolder" Name="SQRT_Gem" />',
        '      </Directory>',
        '',
        '      <!-- Desktop -->',
        '      <Directory Id="DesktopFolder" Name="Desktop" />',
        '    </Directory>',
        '',
        '    <!-- Shortcuts -->',
        '    <DirectoryRef Id="ApplicationProgramsFolder">',
        '      <Component Id="AppShortcuts" Guid="{F984E290-7D51-4091-8D99-A0CD5D8C4217}">',
        '        <Shortcut Id="StartMenuShortcut"',
        '                  Name="SQRT_Gem Calculator"',
        '                  Description="High-Precision Analytical Math Calculator"',
        '                  Target="[INSTALLDIR]SQRT_Gem.exe"',
        '                  WorkingDirectory="INSTALLDIR"',
        '                  Icon="AppIcon.ico" />',
        '        <Shortcut Id="DesktopShortcut"',
        '                  Directory="DesktopFolder"',
        '                  Name="SQRT_Gem Calculator"',
        '                  Description="High-Precision Analytical Math Calculator"',
        '                  Target="[INSTALLDIR]SQRT_Gem.exe"',
        '                  WorkingDirectory="INSTALLDIR"',
        '                  Icon="AppIcon.ico" />',
        '        <RemoveFolder Id="CleanUpProgramMenu" On="uninstall" />',
        '        <RegistryValue Root="HKCU"',
        '                       Key="Software\\SQRT_Gem"',
        '                       Name="Installed"',
        '                       Type="integer"',
        '                       Value="1"',
        '                       KeyPath="yes" />',
        '      </Component>',
        '    </DirectoryRef>',
        '',
        '    <!-- Custom Action: Clean AppData on Uninstall (Section 10 of TZ_1.md) -->',
        '    <CustomAction Id="CleanUserDataAction"',
        '                  Directory="TARGETDIR"',
        '                  ExeCommand="powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File &quot;[INSTALLDIR]uninstall_cleanup.ps1&quot;"',
        '                  Execute="immediate"',
        '                  Return="ignore" />',
        '',
        '    <InstallExecuteSequence>',
        '      <Custom Action="CleanUserDataAction" Before="RemoveFiles">',
        '        (NOT UPGRADINGPRODUCTCODE) AND (REMOVE=&quot;ALL&quot;)',
        '      </Custom>',
        '    </InstallExecuteSequence>',
        '',
        '    <!-- Features -->',
        '    <Feature Id="MainFeature" Title="SQRT_Gem Application" Level="1">',
        '      <ComponentRef Id="MainExecutableCmp" />',
        '      <ComponentRef Id="LicenseCmp" />',
        '      <ComponentRef Id="UninstallCleanupCmp" />',
        '      <ComponentRef Id="AppShortcuts" />',
    ])

    for cid in component_ids:
        xml_lines.append(f'      <ComponentRef Id="{cid}" />')

    xml_lines.extend([
        '    </Feature>',
        '  </Product>',
        '</Wix>',
        ''
    ])

    output_wxs.parent.mkdir(parents=True, exist_ok=True)
    output_wxs.write_text("\n".join(xml_lines), encoding="utf-8")
    print(f"[*] Generated WiX manifest: {output_wxs} ({len(component_ids) + 3} components)")
    return component_ids


def main():
    project_root = Path(__file__).resolve().parent.parent
    dist_dir = project_root / "dist" / "SQRT_Gem"
    exe_file = dist_dir / "SQRT_Gem.exe"

    if not exe_file.exists():
        print(f"[!] PyInstaller distribution not found at {dist_dir}!")
        print(f"[!] Run PyInstaller first.")
        sys.exit(1)

    icon_file = project_root / "packaging" / "icon.ico"
    if not icon_file.exists():
        print(f"[!] Warning: {icon_file} not found!")

    wxs_file = project_root / "packaging" / "product.wxs"
    print(f"[*] Scanning {dist_dir} and generating WiX manifest...")
    generate_wxs(project_root, dist_dir, wxs_file)

    candle, light = find_wix_tools()
    if not candle or not light:
        print("[!] WiX Toolset (candle.exe / light.exe) not found!")
        sys.exit(1)

    out_dir = project_root / "dist_installer"
    out_dir.mkdir(parents=True, exist_ok=True)
    wixobj = out_dir / "product.wixobj"
    msi_out = out_dir / "SQRT_Gem.msi"

    print(f"[*] Compiling with candle.exe: {candle}")
    cmd_candle = [str(candle), "-arch", "x64", "-nologo", str(wxs_file), "-out", str(wixobj)]
    res = subprocess.run(cmd_candle, cwd=project_root, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Candle error:\n{res.stderr}\n{res.stdout}")
        sys.exit(res.returncode)

    print(f"[*] Linking with light.exe: {light}")
    cmd_light = [str(light), "-nologo", "-sval", "-b", str(project_root), str(wixobj), "-out", str(msi_out)]
    res = subprocess.run(cmd_light, cwd=project_root, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Light error:\n{res.stderr}\n{res.stdout}")
        sys.exit(res.returncode)

    # Clean up intermediate files
    wixobj.unlink(missing_ok=True)
    (out_dir / "SQRT_Gem.wixpdb").unlink(missing_ok=True)

    size_mb = msi_out.stat().st_size / (1024 * 1024)
    print(f"[+] SUCCESS! Built 64-bit MSI installer: {msi_out} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
