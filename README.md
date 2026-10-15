# JiuKong Linux — 久空 AI 開發作業系統

面向 Intel x86-64、4 GB RAM、SSD 的 Debian 13（trixie）輕量開發桌面。專案預定儲存庫：`jiukong-labs/jiukong-linux`。

**目前為 0.1.0-dev 工程原型，尚未產出或驗收可發行 ISO。** 這個版本提供實際 live-build 配置、安裝腳本、Tkinter 控制中心、硬體檢查與驗收工具。執行環境為 macOS arm64，ISO 建置與 QEMU 測試仍須在下述環境完成；不能把原始碼檢查當成開機驗證。

採用 Debian 官方核心，不重新編譯。X11、Openbox、LightDM、tint2、PCManFM、xfce4-terminal、NetworkManager、PipeWire、Fcitx5 注音。包含 Firefox ESR 用於文件、AI 登入與官方網頁。保留 AppArmor、核心 OOM、earlyoom、防火牆、自動安全更新。沒有 SSH server、辦公套件或 AI 工具預載映像。

## 快速開始

8 GB Apple Silicon Mac 建議優先使用[雲端建置](docs/cloud-build.md)，避免本機 amd64 模擬工作影響日常操作。已提供手動 GitHub Actions workflow；尚未實際執行雲端 ISO 建置。

已安裝 Docker，可先執行 `./scripts/check-docker.sh`，在 Debian 13 amd64 容器檢查套件相依與 live-build 配置；這項檢查不會產出 ISO。

在乾淨的 **Debian 13 amd64 VM 或實機**，先依 [建置說明](docs/build.md) 安裝建置依賴：

```sh
python3 -m unittest discover -s tests -v
sudo ./build.sh
(cd dist && sha256sum -c *.iso.sha256)
./scripts/test-qemu.sh --iso dist/實際檔名.iso --firmware bios --mode live
./scripts/test-qemu.sh --iso dist/實際檔名.iso --firmware uefi --mode install
./scripts/test-qemu.sh --firmware uefi --mode disk
```

在安裝完成的桌面，以一般使用者執行：

```sh
python3 /usr/local/lib/jiukong/scripts/hardware-check.py --json
/usr/local/lib/jiukong/scripts/install-all.sh
jiukong-control-center
```

Live 模式自動登入 `jiukong`，每次開機產生 6 位數字臨時密碼並在終端機顯示，用於鎖定與 sudo。安裝時建立自己的使用者與密碼，沒有固定萬用密碼。**安裝到 SSD 的格式化可能刪除所有原有資料。請先備份，從開機選單選 Debian Installer，逐項確認磁碟。**

## 文件

- [建置與產物](docs/build.md)、[安裝手冊](docs/install.md)
- [記憶體與效能](docs/memory.md)、[工具來源、簽章與更新](docs/tools.md)
- [QEMU 與 A–Q 驗收](docs/testing.md)、[目前驗證狀態](docs/validation.md)
- [官方來源與授權](docs/sources.md)、[維護方式](docs/maintenance.md)

桌面閒置 300–550 MiB 是待實測的最佳化目標。建置設定固定 Debian 發行代號與專案版本，安全更新來源會變動；不宣稱位元完全相同的重現性。每次建置會輸出套件版本、來源雜湊、日誌及 ISO SHA256。第三方專有工具在使用者安裝時從官方來源下載，登入由使用者自行完成。

本儲存庫原始程式採 MIT；Debian 套件、韌體及第三方工具保留各自授權。此專案不是 Debian、OpenAI、Microsoft 或 Anthropic 的官方發行版。
