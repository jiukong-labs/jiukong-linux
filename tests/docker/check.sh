#!/bin/bash
set -Eeuo pipefail
cd /work
echo '=== Debian amd64 container source validation ==='
test "$(dpkg --print-architecture)" = amd64
./scripts/validate.sh
desktop-file-validate desktop/*.desktop
xmllint --noout desktop/openbox/*.xml
echo '=== Debian package dependency resolution ==='
apt-get -o APT::Update::Error-Mode=any update
python3 - <<'PY'
from pathlib import Path
import subprocess
packages = Path('packages/base.list.chroot').read_text().split()
subprocess.run(['apt-get', '-s', '--no-install-recommends', 'install', *packages], check=True)
PY
echo '=== live-build configuration validation ==='
work=$(mktemp -d)
python3 scripts/prepare-build.py "$work"
cd "$work"
/work/scripts/configure-live.sh
echo '容器檢查通過；尚未建置 ISO 或驗證 BIOS/UEFI 開機。'
