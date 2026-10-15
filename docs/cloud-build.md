# 在雲端建置，讓 Mac 只負責編輯

8 GB Apple Silicon Mac 同時執行開發工具與 amd64 模擬建置時，可能產生明顯記憶體壓力。本次本機建置未完成，Docker API 再次逾時；後續改以原生 x86-64 遠端建置為優先，不再自動重啟本機重負載工作。

## GitHub Actions

已提供 `.github/workflows/build-cloud.yml`。第一次雲端執行通過來源／套件／配置檢查，但建置在掛載 `/proc` 時失敗（exit 32），尚未產出 ISO。這個 workflow 使用 GitHub 提供的 Ubuntu x64 VM，在其中以 Debian 13 amd64 Docker 建置；不是把目標系統改成 Ubuntu，也不需要 Mac 執行 Docker。

1. 將原始碼與 workflow 放到正確的 GitHub 儲存庫。預定目標是 `jiukong-labs/jiukong-linux`；目前本地 origin 仍是 `cloudgate-it/jiukong-linux`，另加 `jiukong` remote 上傳至預定目標，不變更原有 origin。
2. 在 GitHub 的 Actions 選 **Build ISO in GitHub cloud**，按 **Run workflow**。它只會手動啟動，不會每次修改都重建 ISO。
3. workflow 先在一次性的雲端 VM 移除本專案用不到的 Android/.NET/Haskell SDK，檢查至少 25 GiB 空間，再執行套件與配置檢查及 ISO 建置。這段清理僅限 GitHub-hosted VM，不應複製到個人電腦執行。
4. 成功後從該次執行的 Artifacts 下載 `jiukong-development-iso-*`，包含 ISO、SHA256、套件版本與建置資訊；ISO artifact 保留一天，建置日誌保留七天。失敗只提供診斷，不宣稱產出 ISO。
5. 下載後驗證 SHA256。開機與安裝仍須另外在適合的 x86-64 VM／實機完成；雲端建置成功不等於 A–Q 驗收完成。

GitHub 標準 x64 Linux runner 目前在公開儲存庫為 4 核／16 GB、私人儲存庫為 2 核／8 GB；官方列出的 SSD 空間為 14 GB。清理預載 SDK 後仍可能不足，因此 workflow 保留 25 GiB 檢查，空間不足就明確停止，不保證每種 runner 均可建置。

公開儲存庫的標準 runner 執行時間依 GitHub 規則免費；私人儲存庫使用方案分鐘配額，ISO artifacts 也須留意儲存配額與費用。不要為了免費建置而公開尚未確認可公開的內容。此專案不會自動變更可見性、付費方案或建立 Release。

官方依據：[runner 規格](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)、[Actions 計費與儲存](https://docs.github.com/en/billing/concepts/product-billing/github-actions)。查核日期：2026-10-15。

## 既有 x86-64 電腦或遠端 VM

如已有閒置 Intel／AMD 64-bit 電腦，使用 Debian 13 amd64、建議 8 GB RAM 與至少 40 GiB 可用 SSD，直接依 build.md 建置。這是建置主機的建議，目標桌面仍為 4 GB。Mac 可透過 SSH 編輯、查看日誌與下載結果；不需要在 Mac 本機模擬 amd64。

新租用的雲端 VM 需要使用者自行選擇供應商、預算及帳號，本專案不會自動開立付費機器。

## 雲端掛載權限

`build-docker.sh --github-hosted` 僅接受 GitHub-hosted Linux x64 runner（檢查環境與架構），在一次性 VM 內使用 privileged 建置容器。原因是 live-build 必須掛載 proc/devpts 等檔案系統，首輪使用 SYS_ADMIN 仍被 Docker 的掛載限制拒絕。privileged 容器可存取該雲端 VM 的裝置；不得將此模式搬到日常電腦或自架 runner 使用。不掛入主機目錄或 Docker socket，不修改 ISO 內的 AppArmor／核心安全設定。一般入口仍維持 SYS_ADMIN，嚴格主機可能須改用原生 Debian 建置。

依據：[Docker 容器權限說明](https://docs.docker.com/engine/containers/run/#runtime-privilege-and-linux-capabilities)。
