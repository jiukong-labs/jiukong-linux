#!/bin/bash
set -Eeuo pipefail
. "$(dirname -- "${BASH_SOURCE[0]}")/lib/common.sh"
user_system
repo_install claude-code https://downloads.claude.ai/keys/claude-code.asc \
    31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE \
    https://downloads.claude.ai/claude-code/apt/stable stable claude-code
smoke claude --version
echo '請自行執行 claude 登入；不在此腳本儲存任何憑證。'
