# 4 GB 記憶體策略

zram 由 `jiukong-zram.service` 管理，使用 Debian 核心內建 zram 模組，邏輯大小是 `/proc/meminfo` MemTotal 的 50%，不是預留 50% 實體 RAM。優先使用核心實際列出的 lzo-rle，否則使用 lzo，不支援則明確失敗。壓縮後資料才消耗實體 RAM；壓縮效益取決於資料內容。priority=100，SSD swap priority=10。

Live 開機參數與安裝後 GRUB 設定均加入 `zswap.enabled=0`，啟動 zram 前再次檢查；若 zswap 仍開啟則拒絕重疊配置。沒有另裝 zram-tools 或 systemd-zram-generator，避免重複管理。核心 OOM 保留，earlyoom 在可用記憶體與 swap 都低於設定門檻時協助終止程序，避免整個桌面長時間無回應；使用者工作仍應經常儲存。

SSD 使用 Debian Installer 已配置的 swap；若沒有磁碟 swap，`jiukong-swap.service` 在已安裝的 ext4 根目錄建立 2 GiB `/swapfile`，需要剩餘至少 4 GiB。權限 0600，加入 fstab，不覆寫既有檔案。非 ext4／建立中途失敗會回報失敗，必須人工檢查，不能把失敗當成成功。Live 不建立檔案、不以 tmpfs 額外保留大量 RAM。自動建立的 swapfile 不支援休眠到磁碟；一般 suspend 必須實機驗證。

```sh
systemctl status jiukong-zram jiukong-swap earlyoom
zramctl
swapon --show
cat /sys/module/zswap/parameters/enabled
cat /proc/sys/vm/swappiness
journalctl -u jiukong-zram -u jiukong-swap -u earlyoom
```

沒有寫入 swappiness override：保留 Debian 預設，直到有實測依據。先在乾淨 VM 登入後閒置五分鐘，用 guest-check --idle 記錄 MemTotal − MemAvailable。300–550 MiB 是目標，包含中文輸入、網路與安全服務後仍需實測，不是保證。

在相同 VM snapshot、2 核／4 GB、相同工具與檔案下，記錄核心版本、壓縮算法、swap 使用、PSI 與早期 OOM。可顯式測試不同候選值：

```sh
cat /proc/sys/vm/swappiness > original-swappiness.txt
sudo sysctl vm.swappiness=60
./scripts/benchmark.sh --pressure-mib 2304 --seconds 10 --output results/swap-60.json
vmstat 1 30 > results/vmstat-60.txt
```

對 100、150 重複同一工作負載，另測試 VS Code＋單一 AI 工具的互動延遲。壓力測試可能被 OOM 終止，這是測試結果，不應停用保護。每個候選使用乾淨 VM、至少三次，記錄反應時間、swap in/out 與 OOM，不只看 benchmark 吞吐。完成後以原始值還原 `sudo sysctl vm.swappiness=原始數字`。只有結果支持時才新增版本控制下的 sysctl 設定。

調整 swap 請先關閉大型程式，確保 swapoff 有足夠 RAM。不要在記憶體壓力下直接停用 zram。SSD 不強制調整 I/O scheduler、CPU governor、核心安全或開機防護；TRIM 與 suspend／resume 依實機及 Debian 預設驗證。
