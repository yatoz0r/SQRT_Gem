#!/usr/bin/env python3
"""Cross-platform Debian (.deb) package generator in pure Python.

Works on Windows, Linux, and macOS without requiring dpkg-deb or Unix ar utility.
Constructs valid Debian binary package format:
  !<arch>
  debian-binary (2.0\n)
  control.tar.gz (control, postinst, postrm, md5sums)
  data.tar.gz (filesystem hierarchy: usr/, opt/)
"""

import os
import sys
import io
import time
import tarfile
import hashlib
from pathlib import Path


def create_ar_header(name: str, size: int, mtime: int = 0, mode: int = 0o100644) -> bytes:
    """Format an AR archive file header (60 bytes)."""
    ident = (name + "/").ljust(16)
    timestamp = str(int(mtime)).ljust(12)
    owner = "0".ljust(6)
    group = "0".ljust(6)
    file_mode = oct(mode)[2:].rjust(8)
    file_size = str(size).ljust(10)
    trailer = b"`\n"

    header_str = f"{ident}{timestamp}{owner}{group}{file_mode}{file_size}"
    return header_str.encode("ascii") + trailer


def build_tar_gz(items: list) -> bytes:
    """Create in-memory tar.gz from list of (archive_path, source_path_or_bytes, mode)."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for arcname, src, mode in items:
            ti = tarfile.TarInfo(name=arcname)
            ti.mtime = int(time.time())
            ti.uid = 0
            ti.gid = 0
            ti.uname = "root"
            ti.gname = "root"
            ti.mode = mode

            if isinstance(src, bytes):
                ti.size = len(src)
                tar.addfile(ti, io.BytesIO(src))
            elif isinstance(src, Path) and src.is_file():
                data = src.read_bytes()
                ti.size = len(data)
                tar.addfile(ti, io.BytesIO(data))
            elif isinstance(src, Path) and (src.is_dir() or not src.exists()):
                ti.type = tarfile.DIRTYPE
                tar.addfile(ti)
    return buf.getvalue()


def build_deb(project_root: Path, output_deb_path: Path):
    print(f"[*] Building Debian package (.deb) from: {project_root}")
    deb_dir = project_root / "packaging" / "deb"
    
    # 1. Prepare data.tar.gz items
    data_items = []

    # System directories
    for d in ["usr", "usr/bin", "usr/share", "usr/share/applications", 
              "usr/share/icons", "usr/share/icons/hicolor", "usr/share/icons/hicolor/scalable",
              "usr/share/icons/hicolor/scalable/apps", "opt", "opt/sqrt-gem"]:
        data_items.append((f"./{d}", Path(), 0o755))

    # Binary launcher
    launcher = deb_dir / "usr" / "bin" / "sqrt-gem"
    data_items.append(("./usr/bin/sqrt-gem", launcher, 0o755))

    # Desktop file
    desktop = deb_dir / "usr" / "share" / "applications" / "sqrt-gem.desktop"
    data_items.append(("./usr/share/applications/sqrt-gem.desktop", desktop, 0o644))

    # SVG Icon
    svg = deb_dir / "usr" / "share" / "icons" / "hicolor" / "scalable" / "apps" / "sqrt-gem.svg"
    data_items.append(("./usr/share/icons/hicolor/scalable/apps/sqrt-gem.svg", svg, 0o644))

    # Application files in /opt/sqrt-gem
    dist_dir = project_root / "dist" / "SQRT_Gem"
    md5_entries = []

    if dist_dir.exists():
        print(f"[*] Bundling PyInstaller distribution from {dist_dir}...")
        for root, dirs, files in os.walk(dist_dir):
            rel_dir = Path(root).relative_to(dist_dir)
            arc_dir = f"./opt/sqrt-gem/{rel_dir}".replace("\\", "/").rstrip("/.")
            if arc_dir != "./opt/sqrt-gem":
                data_items.append((arc_dir, Path(), 0o755))
            for f in files:
                f_path = Path(root) / f
                arc_file = f"./opt/sqrt-gem/{rel_dir}/{f}".replace("\\", "/").replace("/./", "/")
                data = f_path.read_bytes()
                mode = 0o755 if f_path.suffix == "" or f_path.name.startswith("SQRT_Gem") else 0o644
                data_items.append((arc_file, f_path, mode))
                md5_entries.append(f"{hashlib.md5(data).hexdigest()}  {arc_file[2:]}\n")
    else:
        print("[*] dist/SQRT_Gem not found; packaging Python source and locales into /opt/sqrt-gem...")
        src_dir = project_root / "src"
        locales_dir = project_root / "locales"
        for folder in [src_dir, locales_dir]:
            for root, _, files in os.walk(folder):
                rel = Path(root).relative_to(project_root)
                arc_dir = f"./opt/sqrt-gem/{rel}".replace("\\", "/")
                data_items.append((arc_dir, Path(), 0o755))
                for f in files:
                    f_path = Path(root) / f
                    arc_file = f"{arc_dir}/{f}"
                    data = f_path.read_bytes()
                    data_items.append((arc_file, f_path, 0o644))
                    md5_entries.append(f"{hashlib.md5(data).hexdigest()}  {arc_file[2:]}\n")

    data_tar_gz = build_tar_gz(data_items)

    # 2. Prepare control.tar.gz
    control_items = []
    control_file = deb_dir / "DEBIAN" / "control"
    control_items.append(("./control", control_file, 0o644))

    postinst_file = deb_dir / "DEBIAN" / "postinst"
    if postinst_file.exists():
        control_items.append(("./postinst", postinst_file, 0o755))

    postrm_file = deb_dir / "DEBIAN" / "postrm"
    if postrm_file.exists():
        control_items.append(("./postrm", postrm_file, 0o755))

    md5sums_bytes = "".join(md5_entries).encode("utf-8")
    control_items.append(("./md5sums", md5sums_bytes, 0o644))

    control_tar_gz = build_tar_gz(control_items)

    # 3. Assemble Debian package (ar archive)
    debian_binary = b"2.0\n"

    output_deb_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_deb_path, "wb") as f:
        # AR magic
        f.write(b"!<arch>\n")

        # 1. debian-binary
        f.write(create_ar_header("debian-binary", len(debian_binary)))
        f.write(debian_binary)
        if len(debian_binary) % 2 != 0:
            f.write(b"\n")

        # 2. control.tar.gz
        f.write(create_ar_header("control.tar.gz", len(control_tar_gz)))
        f.write(control_tar_gz)
        if len(control_tar_gz) % 2 != 0:
            f.write(b"\n")

        # 3. data.tar.gz
        f.write(create_ar_header("data.tar.gz", len(data_tar_gz)))
        f.write(data_tar_gz)
        if len(data_tar_gz) % 2 != 0:
            f.write(b"\n")

    print(f"[SUCCESS] Debian package generated: {output_deb_path} ({output_deb_path.stat().st_size} bytes)")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    out = root / "dist_installer" / "sqrt-gem_1.0.0_amd64.deb"
    build_deb(root, out)
