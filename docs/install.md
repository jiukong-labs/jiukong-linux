# 繁體中文安裝手冊

**磁碟格式化可能刪除所有原有資料。先備份，再確認目標磁碟型號、容量與裝置名稱。** 本專案沒有自製磁碟清除器，也不會從控制中心開始格式化。

1. 先在 Debian 13 建置 ISO 並依 `docs/testing.md` 完成 BIOS／UEFI Live 與虛擬磁碟安裝。未驗收的開發 ISO 不應交給一般使用者直接安裝。
2. 使用 `sha256sum -c 對應.iso.sha256` 驗證映像；macOS 可用 `shasum -a 256 映像.iso` 比對。SHA256 檔須從可信來源取得。
3. 使用經確認的映像寫入工具把 hybrid ISO 寫入 USB。工具會覆寫 USB 資料，必須人工確認 USB 型號與容量。本專案刻意不提供 `dd /dev/...` 自動寫入命令。
4. 從電腦韌體選 USB 開機，先試 Live。若 Intel 顯示失敗，可臨時在開機參數加入 `nomodeset` 診斷，這會犧牲加速，不是全機預設。
5. Live 自動登入 `jiukong`。終端機顯示本次密碼，亦可 `cat /run/jiukong-live-password` 查看。其他使用者不可讀取此檔；重開機會重設。保護好實體 USB 與試用環境。
6. 執行硬體檢查工具，測試顯示、網路、鍵盤、觸控板、音訊、休眠喚醒。`Super+Space` 開控制中心、`Super+Enter` 開終端、`Super+L` 鎖定。Fcitx5 用 Ctrl+Space 切換，預設注音；若無候選窗，用 fcitx5-configtool 檢查 Chewing。
7. 安裝必須重新開機，從 ISO 選單選 Debian Installer 的 Install／Graphical Install。確認繁體中文、台北時區，建立自己的帳號與強密碼。root 帳號不開放直接登入；第一位使用者由 Debian Installer 配置 sudo。
8. 選正確 SSD。4 GB RAM 建議 ext4；UEFI 保留或建立 EFI System Partition，Legacy BIOS 依 Installer 提示配置 GRUB。需要加密者可使用 Debian Installer 提供的加密 LVM；必須個別驗收。雙系統請使用手動分割，勿選整顆磁碟。
9. 在寫入分割表的最終確認頁，再次核對裝置。按確認可能刪除全部原有資料。沒有任何 preseed 自動確認此步驟。
10. 安裝完成，移除 ISO／USB，從 SSD 開機，使用新帳號登入。確認 Live 帳號已移除、未保留自動登入／免密碼 sudo，檢查 `sudo -l`。這些是發行前必驗項目。
11. 未建立磁碟 swap 時，第一次 SSD 開機會在 ext4 根目錄建立 2 GiB `/swapfile`；若 Installer 已建立 swap 則保留它。Live 模式不會建立 SSD swap。其他檔案系統見記憶體文件。
12. 執行系統更新，再以一般使用者執行 `install-all.sh`。每個工具自行登入，登入憑證不放入 ISO。4 GB 建議一次只開一個大型 AI 桌面程式。

英文介面：在 LightDM 登入畫面選擇 English；若未顯示語言選項，可在使用者 `~/.profile` 加入 `export LANG=en_US.UTF-8` 後重新登入。系統已產生兩種 locale，注音可保留。

需要網路時由 nm-applet 選 Wi-Fi，輸入自己的密碼。SSH server 未預裝；如需遠端管理，應自行安裝、配置金鑰及防火牆規則，勿直接對外開放密碼登入。
