# 驗證紀錄 — 2026-10-15

目前狀態：**工程原型，未通過發行驗收**。尚未建立 ISO、沒有可提供的 ISO SHA256、沒有 BIOS／UEFI／SSD 安裝成功結果，亦未量測目標桌面 RAM。

## 已實際執行

主機：macOS Darwin 27、arm64、一般使用者 UID 501、8 GiB RAM。初次驗證時沒有可用的 Linux 建置環境，Docker daemon 查詢失敗；後續已恢復 Docker API，並完成下述容器驗證。

## Docker 後續驗證

操作者後續回報 Mac 幾乎當機，已停止新增本機重負載工作，改準備手動雲端建置流程。嘗試停止本專案建置容器的 Docker stop 命令在 15 秒內未回應，**無法確認容器已停止**；已請操作者正常退出 Docker Desktop。雲端 workflow 已推送並執行首輪，詳見下節；沒有雲端 ISO 產物。

- 正常重啟 Docker Desktop 逾時後，以 SIGTERM 正常終止殘留程序，再重新開啟，`/_ping` 已回傳 OK。沒有清除映像、資料卷或重設 Docker。
- 已實際建立並執行 Debian 13 `linux/amd64` 容器：13 項測試、Debian ShellCheck 0.10.0、desktop-file-validate、XML 語法、全部映像套件的 APT 相依模擬、實際 `lb config` 均通過。
- 首次容器測試發現模擬環境對不存在的執行檔可能回傳 127，未丟出 Python ENOENT 例外；已修正命令查詢，重跑後通過。
- 通過紀錄：`logs/docker-check-20261015T012258Z.log`。檢查映像 ID：`sha256:072e5df53e4ccefc728356a1c5814db80330feaf81a380cf92a383bdc74ab1bc`。這是當時原始碼的檢查證據，不代表後續任意改動自動通過。
- 容器增加 SYS_ADMIN 後，proc 掛載／卸載測試已通過，沒有使用 privileged 模式或主機目錄／裝置掛載。
- 已啟動第一個實際 live-build 建置。Debian Release 簽章已通過，amd64 chroot 已執行 dpkg；後續輸出停在 `Unpacking libstdc++6:amd64`，超過九分鐘沒有新輸出。Docker info/top/exec 先後逾時，最新健康檢查在 20 秒後明確失敗，無法確認容器內程序的最終狀態。**目前尚未產出 ISO**。建置容器為 `jiukong-build-20261015T012547Z`，主機日誌為 `logs/docker-build-20261015T012547Z.log`；未刪除該建置容器。
- 主機當時 swap 使用約 7.3 GiB，未在最近的 Docker VM console 記錄中看到 OOM-kill；不能僅憑 swap 使用量判定根因。macOS 拒絕讀取 Docker settings-store，因此已向操作者詢問 Resources 的 Memory／CPUs 設定，尚未修改全域資源設定，也沒有關閉其他專案的程式。
- 已加入有 20 秒上限的共用 Docker 健康檢查，讓後續入口在引擎失去回應時明確報錯。最新原始碼在主機再次通過 13 項測試、ShellCheck 及 Python compileall；這不代表已完成容器整合或開機驗收。
- 原生 arm64 QEMU 測試映像建置因主機回應變慢而主動取消，讓 ISO 建置優先；尚未執行 QEMU 開機。沒有把取消的映像建置標示為成功。

- `python3 -m unittest discover -s tests -v`：13 項通過。驗證記憶體與 CPU 資料解析、跨核心 ISA 交集、CPU guest tick 計算、命令錯誤處理、VS Code JSONC 保留及安全預設、staging 產物、人工分割限制、Codex 鎖檔與腳本／XML 語法。
- Python compileall：通過；不代表 Tk 視窗已在 Debian 執行。
- ShellCheck 0.11.0 darwin.aarch64：全部 Bash、chroot hook 與 Live 密碼元件在 warning 等級通過。工具下載於 /tmp，未安裝至系統。
- Debian trixie 官方 main/non-free-firmware amd64 Packages 索引：套件名稱逐一可找到。這是名稱查核；尚未在 Debian APT 模擬完整相依解析。曾發現 `policykit-1` 已不可用，已改用 `polkitd`。
- 唯讀解開 Debian 官方 live-config、live-config-systemd 套件：確認 `user-setup` 必須明列、元件載入路徑為 `/usr/lib/live/config`、預設 sudo／polkit 無提示規則的移除位置。尚未測試真正開機。
- Microsoft、Anthropic、OpenAI 官方公開金鑰的主指紋與安裝器設定一致（本機解析 OpenPGP 主金鑰封包比對；尚未在本機跑 Debian GPG/APT 交易）。
- 在 /tmp 暫存目錄用鎖檔執行 npm ci --ignore-scripts，再執行 npm audit signatures：2 個套件的 registry signatures 與 attestations 均通過。這是 macOS arm64 的 root／平台 optional dependency，**不是 Linux amd64 Codex 的啟動測試**。
- hardware-check.py 在 macOS 回報不符 Linux／amd64／CPU flags，exit 2；沒有誤報為支援。
- benchmark.sh --seconds 1 在主機完成有限 CPU、128 MiB 記憶體複製與暫存檔 I/O。僅驗證測試工具可執行，不作為目標工作站效能數據。
- build.sh 在 macOS 明確失敗；test-qemu.sh 回報缺少 qemu-system-x86_64；install-all.sh 拒絕非 Linux amd64。三者均未執行安裝／建置或改寫主機系統設定。

本機原始輸出位於未追蹤的 `results/source-checks.log`、`results/host-hardware.json`、`results/host-benchmark.json`。這些不是可發行產物。雲端來源檢查已執行，完整 ISO 建置尚未通過。

## 八階段狀態

| 階段 | 已提供實作 | 整合驗證狀態 |
| --- | --- | --- |
| 1 Minimal＋Openbox ISO | live-build、官方核心、BIOS／UEFI、Debian live installer | lb config 已通過；實際建置輸出停滯、Docker API 逾時；尚未開機 |
| 2 繁中桌面與安全更新 | locale、Fcitx5、網路／音訊／鎖定、APT security、nftables | APT 相依模擬已通過；桌面與服務未測 |
| 3 記憶體 | zram 50%、可用算法檢查、zswap 排除、ext4 swapfile、earlyoom | 尚未在 Linux 啟用或壓力測試 |
| 4 開發工具 | 官方 VS Code／Claude Code APT、Codex npm lock、IDE 設定 | 設定與 npm macOS 簽章已測；Linux 未測 |
| 5 桌面 AI 工具 | 官方 ChatGPT／Claude Desktop signed APT 安裝器 | 官方流程與 key 查核；未安裝／啟動 |
| 6 控制中心 | Python Tkinter、非 root、授權操作交由終端機 sudo | Python 語法已測；Debian GUI 未測 |
| 7 驗收 | QEMU Live／install／disk、硬體報告、benchmark、A–Q 報告 | 測試工具部分已測；目標驗收未測 |
| 8 發行 | 成功建置後的 SHA256／日誌／套件版本、手冊、手動 build workflow | 尚無 ISO／Release；未執行發行授權審查 |

## A–Q 目前結果

A–Q **全部尚未在目標機或 QEMU 驗證**。沒有「模擬成功」或「實測成功」項目。F/G/H/I/J/K 的完整帳號功能需要使用者登入後進行實機測試；CLI --version 與 GUI 起動可先在無帳號環境獨立驗證。

套件相依與 lb config 已在 Debian 13 amd64 容器完成驗證。後續須完成 ISO 建置，對 BIOS、UEFI 各執行 Live→安裝→移除 ISO→重新登入，之後才能評估 RAM、swappiness 與 Intel 實機相容性。

## 首次 GitHub 雲端建置

[Run 38671537652](https://github.com/jiukong-labs/jiukong-linux/actions/runs/38671537652)，commit `e3c52b6`：來源測試、APT 相依模擬、lb config 通過；Debian 基礎系統成功安裝，chroot 階段掛載 devpts／proc 失敗，exit 32。這是建置失敗，artifact 僅為日誌，沒有 ISO。後續將較高掛載權限限制於 GitHub 一次性 VM 的專用參數，等待重新建置驗證；不在 Mac 重新執行 Docker。
