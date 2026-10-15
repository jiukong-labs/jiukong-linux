#!/bin/bash
set -Eeuo pipefail
. "$(dirname -- "${BASH_SOURCE[0]}")/lib/common.sh"
user_system
if ! command -v npm >/dev/null; then
    apt_refresh
    sudo apt-get install nodejs npm
fi
node -e 'if (Number(process.versions.node.split(".")[0]) < 20) process.exit(1)' || fail '需要受支援的 Node.js >=20；建議 Debian 13 的 Node.js 20。'
runtime="$HOME/.local/share/jiukong/codex"
mkdir -p "$runtime"
cp "$PROJECT_DIR/config/codex/package.json" "$PROJECT_DIR/config/codex/package-lock.json" "$runtime/"
# Integrity-locked dependencies; do not run package lifecycle scripts.
(cd "$runtime" && npm ci --ignore-scripts --registry=https://registry.npmjs.org --no-fund --no-audit)
# Verify npm registry signatures/provenance before exposing the launcher.
(cd "$runtime" && npm audit signatures --registry=https://registry.npmjs.org)
launcher="$HOME/.local/bin/codex"
if [[ -e $launcher || -L $launcher ]]; then
    [[ $(readlink "$launcher") == "$runtime/node_modules/.bin/codex" ]] || fail "$launcher 已存在，請先檢查既有安裝。"
fi
ln -sfn "$runtime/node_modules/.bin/codex" "$launcher"
smoke "$launcher" --version
"$launcher" --version | tee -a "$HOME/.local/state/jiukong/installed.log"
echo '請重新開啟終端機後執行 codex 自行登入。更新由版本鎖控制，見 docs/tools.md。'
