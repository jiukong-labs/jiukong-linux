# QEMU 與驗收

## Docker 路徑

macOS 未安裝 QEMU、但已安裝 Docker 時，`scripts/test-qemu.sh` 會轉用 `scripts/test-qemu-docker.sh`。參數相同；QEMU 本身使用 Docker daemon 的原生架構，客體仍為 x86-64、2 核、4 GiB。此路徑使用 TCG，不宣稱 KVM 或 Intel 實機驗證。

工具建立獨立的 Debian QEMU 映像，將 ISO 複製到新容器，不掛載主機目錄或裝置。虛擬磁碟保存在 `jiukong-qemu-名稱-韌體` 的專案專用 Docker volume，供 install→disk 測試延續使用。既有虛擬磁碟不覆寫；不要同時啟動兩個使用同一磁碟的 VM。

成功啟動程序後會印出容器名稱與 `127.0.0.1:連接埠`；可用 macOS 螢幕共享連線 `vnc://127.0.0.1:連接埠`。先在 guest 正常關機，再執行下一個模式。啟動程序成功不等於到達桌面或安裝驗收成功。第一次使用會下載 QEMU 相依套件；目前開機驗證狀態以 validation.md 為準。

## 直接執行 QEMU

在 Debian 主機安裝 `qemu-system-x86 qemu-utils ovmf`。`scripts/test-qemu.sh` 固定 2 核、4096 MiB，KVM 有權限時用 host CPU，否則 TCG＋qemu64。TCG 結果須註明模擬，不能當舊 Intel 實測。virtio qcow2 與 cache=none 用於模擬 SSD 環境，速度仍取決於宿主；不代表任何特定 SSD 或 Intel GPU。

```sh
./scripts/test-qemu.sh --iso dist/檔名.iso --firmware bios --mode live --name acceptance
./scripts/test-qemu.sh --iso dist/檔名.iso --firmware bios --mode install --name acceptance
./scripts/test-qemu.sh --firmware bios --mode disk --name acceptance
# 對 --firmware uefi 完整重複一次；不同韌體使用不同 VM 磁碟。
```

Live 模式不接磁碟。install 模式首次建立專案專用 32 GiB qcow2，從 ISO 選 Debian Installer。disk 模式移除 ISO 從同一虛擬磁碟重開。這些命令不接實體磁碟、不自動分割、不把 QEMU 結束碼當驗收。保留 `.build/qemu/*/serial.log`、launch.log 與畫面截圖。螢幕主要輸出至圖形 console，serial.log 未必包含完整 boot log；在 guest 額外保存 journalctl -b。

guest 執行：

```sh
cd /usr/local/lib/jiukong
python3 tests/guest-check.py --environment qemu --idle --output ~/acceptance-live.json
# 安裝工具後另存一份 installed 報告。勿把開啟工具後的 RAM 記為 idle。
```

| ID | 驗證方式 |
| --- | --- |
| A | 開機到 systemd；檢查 degraded units 與 journalctl -b，修正失敗服務 |
| B | LightDM、Openbox 視窗、選單、終端、鎖定與解鎖均可操作 |
| C | nmcli、DNS 與官方 HTTPS 實際請求；另測 Intel 實機 Wi-Fi |
| D | 登入閒置五分鐘，MemTotal − MemAvailable，保留 MiB 與測量條件 |
| E | code 開啟視窗、編輯 Git 專案，自動儲存；不得加 --no-sandbox |
| F/G | VS Code Developer: Show Running Extensions 檢查兩個官方 ID 已 activation，另驗證登入後功能 |
| H/I | CLI --version；再自行登入、送出小型任務，記錄結果 |
| J/K | 桌面視窗啟動、登入、發送訊息；未登入標 needs_login，不能宣稱完整可用 |
| L | 終端、PCManFM、VS Code 以注音輸入「久空測試」，切換英文 |
| M | zram 50%、algorithm、priority，SSD swap；壓力下資料使用增加、PSI 與 OOM 策略正常 |
| N | sudo unattended-upgrade --dry-run --debug 及實際更新交易，檢查 apt timers、來源簽章 |
| O | BIOS／UEFI 各自 ISO Live 到桌面 |
| P | Debian Installer 寫入專用 qcow2 完成，不影響宿主磁碟 |
| Q | 拔除 ISO 後開機、新帳號登入、sudo、鎖定；Live 帳號與免密 sudo 已移除 |

自動工具只判定可證明的部分。A 的 degraded 不代表全部正常，會記 failed 以強制調查。M 僅啟用時標 needs_pressure_test，F/G 的 extension 清單不代表載入。每個人工項目需要具體證據：

```sh
python3 tests/record-result.py ~/acceptance-live.json B pass \
  --evidence 'BIOS Live 登入後確認 Openbox、終端機及鎖定解鎖；截圖 B-live.png'
python3 tests/record-result.py ~/acceptance-live.json J needs_login \
  --evidence 'ChatGPT 視窗已開啟；無使用者帳號，登入與訊息功能等待實機測試'
```

狀態明確區分 measured_pass（實機）、simulated_pass（QEMU）、measured/simulated_measurement（僅數值）、partial、needs_pressure_test、needs_login、failed、untested。預設未知不會變成成功。硬體報告、工具版本、開機模式、ISO SHA256、安裝前後報告應一同保留。

效能測試 `./scripts/benchmark.sh` 在自己的暫存檔測 CPU SHA256、記憶體複製與 fsync 寫入，不寫 raw device。Live overlay 與 cache read 不代表 SSD 實際速度。壓力測試與 swappiness 候選比較見 memory.md。Intel iGPU、休眠喚醒、Wi-Fi、電池與低階 CPU 指令集仍需目標機器；虛擬機成功不能替代。
