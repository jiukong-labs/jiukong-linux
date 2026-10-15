#!/bin/bash
set -Eeuo pipefail
. "$(dirname -- "${BASH_SOURCE[0]}")/lib/common.sh"
user_system
# Same signed apt repo embedded by the official .deb postinst. Key is fetched
# from the official versioned release, fingerprint reviewed in official installer.
repo_install chatgpt \
    https://persistent.oaistatic.com/codex-app-prod/linux/arch/26.1007.71326/repository-signing-key.gpg \
    3BFA0E4AE8B8CC16A2D9BA684A3B4A566C4660E4 \
    https://persistent.oaistatic.com/codex-app-prod/linux/deb stable chatgpt
command -v chatgpt
python3 "$SCRIPT_DIR/disable-tool-autostart.py" chatgpt
echo 'ChatGPT Linux preview 已安裝；請在桌面啟動並自行登入。'
