# AI 工具安裝與更新

所有安裝腳本以一般使用者執行，僅 APT 來源寫入及套件操作用 sudo。不允許 root 執行整個桌面或 Codex。APT 保留確認頁、簽署驗證與正常 sandbox；不使用 `--no-sandbox`、不停用 Workspace Trust。首次安裝可查看官方網站與條款，再確認 APT 安裝。

| 工具 | 來源與驗證 | 更新 |
| --- | --- | --- |
| VS Code | Microsoft signed APT、固定主金鑰指紋 | update-system.sh |
| Codex CLI | 官方 @openai/codex npm，固定 0.162.1，lockfile integrity、npm audit signatures | 更新鎖檔後重跑 install-codex.sh |
| Claude Code | Anthropic stable APT，固定簽署指紋 | update-system.sh |
| ChatGPT Desktop | 官方 Linux preview 的 signed APT | update-system.sh |
| Claude Desktop | Anthropic Linux beta stable APT，固定簽署指紋 | update-system.sh |

ChatGPT 使用官方 .deb postinst 中的同一個 APT repo，金鑰取自官方固定版 release 並比對官方 installer 中的指紋，避免以未驗證 .deb 啟動有 root 權限的 maintainer scripts。官方桌面套件不進 ISO。APT 會驗證 repository metadata 簽章與套件雜湊，若金鑰輪替就停止，待維護者查核後更新指紋。

VS Code 由官方 Marketplace 安裝 `openai.chatgpt`、`anthropic.claude-code`、`MS-CEINTL.vscode-language-pack-zh-hant`。傳輸信任官方 VS Code／Marketplace 的驗證鏈；沒有宣稱本專案另有每份 VSIX 的獨立離線簽章。已存在的使用者 JSONC 設定不覆寫，另放 `jiukong-settings.json` 讓使用者合併。首次建立時啟用繁體中文、Git、自動儲存，減少 minimap、動畫、目錄監看與 terminal scrollback。CLI --version 只證明程序可啟動；擴充套件是否實際 activate 需在桌面驗收。

Codex 使用 Debian Node.js/npm，`npm ci --ignore-scripts` 安裝固定依賴，然後 `npm audit signatures` 驗證 registry 簽章／provenance，成功才建立 launcher。各平台 optional dependency 均在 lockfile，Linux amd64 安裝對應二進位。不使用 sudo npm。一般 profile 應將 `~/.local/bin` 放入 PATH，新開終端後即可呼叫 codex。Ubuntu／其他發行版尚未驗收，安裝器限定 Debian 13 amd64。

維護者更新 Codex 鎖檔（這個動作會改變交付版本，必須 review）：

```sh
npm install --package-lock-only --ignore-scripts --prefix config/codex \
  --registry=https://registry.npmjs.org --save-exact @openai/codex@經審核的版本
# 在 Debian 測試安裝、簽章、--version，再做 Git diff 審查與提交。
```

APT 工具追蹤各官方 stable，實際版本寫入 `~/.local/state/jiukong/installed.log`。不宣稱第三方工具可 bit-for-bit 重現；要凍結部署需另行保存合法可用的版本來源與完整簽署 metadata，不要把專有二進位重新散布。

CLI 自行執行 `codex`／`claude` 登入。桌面自行開啟 `chatgpt`／`claude-desktop`。本專案不讀取 Token、API Key 或帳密。安裝後遮罩工具的 XDG autostart 項目，不由 Openbox 啟動；如果工具日後更新產生新的自動啟動機制，須再次驗證。4 GB 勿同時啟動所有 Electron 工具。Claude Cowork 至少 8 GB，不列入本機支援範圍。
