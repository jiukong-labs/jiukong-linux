#!/bin/bash
set -Eeuo pipefail
. "$(dirname -- "${BASH_SOURCE[0]}")/lib/common.sh"
user_system
repo_install claude-desktop https://downloads.claude.ai/claude-desktop/key.asc \
    31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE \
    https://downloads.claude.ai/claude-desktop/apt/stable stable claude-desktop
command -v claude-desktop
python3 "$SCRIPT_DIR/disable-tool-autostart.py" claude
echo 'Claude Desktop Linux beta 已安裝；請在桌面開啟並登入。Cowork 需要 8 GB RAM，不列入 4 GB 驗收。'
