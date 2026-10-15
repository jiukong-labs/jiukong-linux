#!/usr/bin/env python3
"""Stage source into a fresh live-build directory; never edits the host OS."""
import hashlib
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parent.parent

def prepare(work):
    work = Path(work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    if any(work.iterdir()):
        raise ValueError("工作目錄必須為空，避免覆寫既有建置")
    shutil.copytree(ROOT / "config", work / "config")
    shutil.copytree(ROOT / "packages", work / "config/package-lists")
    image = work / "config/includes.chroot"
    target = image / "usr/local/lib/jiukong"
    for directory in ("scripts", "applications", "desktop", "docs", "tests", "config"):
        shutil.copytree(ROOT / directory, target / directory, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "node_modules"))
    for item in ("README.md", "LICENSE"):
        shutil.copy2(ROOT / item, target / item)
    skel = image / "etc/skel/.config"
    shutil.copytree(ROOT / "desktop/openbox", skel / "openbox", dirs_exist_ok=True)
    shutil.copytree(ROOT / "desktop/tint2", skel / "tint2", dirs_exist_ok=True)
    apps = image / "usr/share/applications"
    apps.mkdir(parents=True, exist_ok=True)
    for file in (ROOT / "desktop").glob("*.desktop"):
        shutil.copy2(file, apps / file.name)
    binary = image / "usr/local/bin"
    binary.mkdir(parents=True, exist_ok=True)
    launcher = binary / "jiukong-control-center"
    launcher.write_text('#!/bin/sh\nexec python3 /usr/local/lib/jiukong/applications/control_center.py "$@"\n')
    launcher.chmod(0o755)
    manifest = []
    for directory in ("config", "packages", "scripts", "applications", "desktop", "tests", "docs"):
        for f in sorted((ROOT / directory).rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts and "node_modules" not in f.parts:
                manifest.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}")
    for name in ("build.sh", "README.md", "LICENSE"):
        f = ROOT / name
        manifest.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {name}")
    contents = "\n".join(manifest) + "\n"
    (work / "config/jiukong-source.sha256").write_text(contents)
    stored = image / "usr/share/jiukong/source.sha256"
    stored.parent.mkdir(parents=True, exist_ok=True)
    stored.write_text(contents)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: prepare-build.py EMPTY_DIRECTORY")
    prepare(sys.argv[1])
