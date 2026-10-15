#!/bin/bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"
python3 -m unittest discover -s tests -v
python3 -m compileall -q applications scripts tests
if command -v shellcheck >/dev/null; then
    # Separate library paths are computed at runtime; SC1091 cannot follow them.
    shellcheck -S warning -e SC1091 build.sh scripts/*.sh scripts/lib/*.sh config/hooks/live/*.chroot config/includes.chroot/usr/lib/live/config/*
else
    echo '尚未執行 ShellCheck：此主機未安裝；CI 必須執行。'
fi
