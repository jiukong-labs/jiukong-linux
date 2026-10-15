#!/usr/bin/env python3
"""Mask vendor XDG autostart entries per user, without changing vendor files."""
from pathlib import Path
import sys

if len(sys.argv) != 2 or sys.argv[1] not in {"claude", "chatgpt"}:
    sys.exit("usage: disable-tool-autostart.py claude|chatgpt")
name = sys.argv[1]
folder = Path.home() / ".config/autostart"
folder.mkdir(parents=True, exist_ok=True)
for base in (Path("/etc/xdg/autostart"), folder):
    for f in base.glob("*.desktop"):
        if name in f.name.lower() or name in f.read_text().lower():
            # Hidden=true overrides system entry with same basename.
            (folder / f.name).write_text("[Desktop Entry]\nType=Application\nName=Disabled AI autostart\nHidden=true\n")
