#!/bin/bash
set -Eeuo pipefail
. "$(dirname -- "${BASH_SOURCE[0]}")/lib/common.sh"
user_system
# VS Code key published by Microsoft; fingerprint is checked before apt trusts it.
repo_install vscode https://packages.microsoft.com/keys/microsoft.asc \
    BC528686B50D79E339D3721CEB3E94ADBE1229CF \
    https://packages.microsoft.com/repos/code stable code
smoke code --version
for extension in openai.chatgpt anthropic.claude-code MS-CEINTL.vscode-language-pack-zh-hant; do
    code --install-extension "$extension"
done
python3 "$SCRIPT_DIR/configure-vscode.py"
code --list-extensions --show-versions | tee "$HOME/.local/state/jiukong/vscode-extensions.txt"
echo '已安裝；擴充套件啟動及帳號登入需在 VS Code 內驗收。'
