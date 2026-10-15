#!/bin/bash
set -Eeuo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
for tool in vscode codex claude-code chatgpt claude-desktop; do
    echo "安裝 $tool"
    "$here/install-$tool.sh"
done
echo '所有安裝命令成功；桌面啟動、擴充套件載入與登入驗收仍須手動執行。'
