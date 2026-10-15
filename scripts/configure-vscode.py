#!/usr/bin/env python3
"""Create low-memory defaults without destroying existing JSONC settings."""
import json
from pathlib import Path

DEFAULTS = {
    "files.autoSave": "afterDelay", "files.autoSaveDelay": 1500,
    "editor.minimap.enabled": False, "editor.smoothScrolling": False,
    "workbench.list.smoothScrolling": False, "extensions.autoUpdate": True,
    "git.enabled": True, "security.workspace.trust.enabled": True,
    "files.watcherExclude": {"**/node_modules/**": True, "**/.git/objects/**": True,
                             "**/.venv/**": True, "**/.build/**": True},
    "search.exclude": {"**/node_modules": True, "**/.venv": True, "**/.build": True},
    "terminal.integrated.scrollback": 1000, "typescript.disableAutomaticTypeAcquisition": True
}

def configure(home):
    folder = Path(home) / ".config/Code/User"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "settings.json"
    if path.exists():
        # JSONC belongs to the user. Supply a separate importable preset.
        (folder / "jiukong-settings.json").write_text(json.dumps(DEFAULTS, indent=2) + "\n")
        print("保留既有 JSONC；請手動合併", folder / "jiukong-settings.json")
    else:
        path.write_text(json.dumps(DEFAULTS, indent=2) + "\n")
    argv = Path(home) / ".vscode/argv.json"
    if not argv.exists():
        argv.parent.mkdir(parents=True, exist_ok=True)
        argv.write_text(json.dumps({"locale": "zh-tw"}, indent=2) + "\n")
    else:
        print("保留既有 argv.json；可從 Configure Display Language 選擇繁體中文。")

if __name__ == "__main__":
    configure(Path.home())
