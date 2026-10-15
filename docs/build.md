# 建置 Live ISO

## 先用 Docker 檢查

macOS 或 Linux 已安裝 Docker 時，可先執行：

```sh
./scripts/check-docker.sh
```

這會建立 Debian 13 amd64 檢查映像，執行原始碼測試、桌面檔案驗證、APT 套件相依模擬，以及實際 `lb config` 驗證。Apple Silicon 使用 amd64 模擬執行。日誌保存在 `logs/docker-check-*.log`，任何步驟失敗都會停止。

檢查容器不掛載主機目錄、不掛載 Docker socket、不使用 privileged 模式。這個流程只做建置前驗證。引擎 API 必須能回應，Docker Desktop 的視窗已開啟不代表 API 正常。

## Docker ISO 建置

```sh
./scripts/build-docker.sh
```

此路徑提供 Debian 13 amd64 使用者空間，在 Apple Silicon 透過 Docker 的 amd64 模擬執行。建置容器只增加 `SYS_ADMIN`，用於 live-build 在容器自己的 namespace 掛載 proc/dev；沒有使用 privileged 模式，也沒有掛載主機目錄、主機裝置或 Docker socket。這是建置環境所需能力，不會加入最終 ISO 或變更桌面安全預設。

每次建立新的專案專用容器。失敗時保留容器與 `logs/docker-build-*.log`，可用輸出中的名稱執行 `docker logs 容器名稱`；不要移除其他專案的容器或資料卷。成功後才複製 ISO、SHA256 及 buildinfo 到主機 `dist/`，驗證 SHA256，再移除這次成功的建置容器。主機至少需要 25 GiB 真實可用空間，Docker VM 的虛擬剩餘容量不能代替主機空間。

Docker 建置結果仍須另外測試 BIOS／UEFI、安裝與登入；amd64 容器成功不等於核心開機成功。原生 Debian amd64 主機仍是較直接的建置及硬體相容性驗證路徑。

## 建置主機

只在 Debian 13 amd64 主機或 VM 建置。建議建置 VM 4 核、8 GB RAM、至少 25 GiB 空間（建議 40 GiB）。使用者的目標桌面仍是 2 核、4 GB。不要把建置工具裝入最終桌面。

```sh
sudo apt-get update
sudo apt-get install live-build debootstrap debian-archive-keyring xorriso squashfs-tools \
  isolinux syslinux-common syslinux-utils grub-pc-bin grub-efi-amd64-bin \
  grub-efi-amd64-signed shim-signed mtools dosfstools rsync git python3 \
  ca-certificates curl cpio gzip xz-utils zstd file util-linux
python3 -m unittest discover -s tests -v
sudo ./build.sh
```

`build.sh` 先檢查作業系統、架構、root、命令、空間與建置鎖。在 `.build/run-*` 新目錄組裝配置，使用 `lb config` 和 `lb build`；錯誤會停止並保留日誌與工作目錄。沒有修改或編譯核心。BIOS 使用 syslinux，UEFI 使用 grub-efi；Secure Boot 交由 live-build auto 與 Debian 簽署套件處理，仍需個別測試，不宣稱已支援所有韌體。

Debian Installer 使用 `--debian-installer live` 把 Live 系統複製到目標磁碟，保留桌面；不是會安裝成普通 Debian 的 netinst 路徑。preseed 只設定語系、時區及停用 root 登入，不預填磁碟、分割確認或密碼。BIOS 與 UEFI 開機選單都必須人工驗證 installer 項目。

輸出在 `dist/`：ISO、`.iso.sha256`、`.iso.packages`、`.iso.source.sha256`、`.iso.buildinfo`、`.iso.build.log`。`logs/` 保留失敗日誌。SHA256 是完整性檢查，正式發行時維護者應另外離線簽署 checksum；本專案不內嵌簽署私鑰。

`config/version.env` 固定專案版本、Debian trixie、時間戳與 HTTPS 官方鏡像。套件經 Debian Archive 金鑰驗證；來源會取得最新安全修補，不是 snapshot 固定版。`SOURCE_DATE_EPOCH` 只減少時間差異；installer、套件更新與工具版本仍會影響產物，不能宣稱 bit-for-bit reproducible。要做完全相同產物研究，需另外鎖定經簽署的 Debian snapshot、安全來源與建置工具，並測試兩次雜湊。

macOS arm64：可使用上述 Docker 路徑，或建立 Debian 13 amd64 VM（跨架構會較慢），把原始碼複製到 VM 的本機 ext4 磁碟後建置。不要在 macOS 使用 sudo 執行 Linux 套件腳本。CI 靜態檢查不會宣稱完成 ISO。

失敗後先看 `logs/build-*.log`。保留工作目錄供除錯；不提供會自動清除既有檔案的 clean 命令。刪除前必須確認沒有殘留 chroot mount。建置完成後也需自行檢查及卸載殘留 mount，不能直接強制刪除。
