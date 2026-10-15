# 維護

使用 trixie 代號，不跟隨下一版 stable。每月重建、跑 BIOS／UEFI Live 與完整虛擬磁碟安裝。安全修補發生時提早重建。Debian unattended-upgrades 僅自動安裝 Debian security origin；不自動重開機。第三方 APT 更新由控制中心手動執行 update-system.sh，逐筆確認。

升版前備份使用者檔案、保存 ISO SHA256、套件清單、硬體報告與測試結果。`apt-get upgrade` 不自動移除套件；需要 full-upgrade 時由維護者審查，不把它放入無提示的桌面動作。不得刪除系統服務或停用安全策略來達到 RAM 數字。

`config/includes.chroot` 是作業系統檔案來源，`desktop/` 是新帳號預設，`applications/` 是無 root 控制中心。修改這些檔案後重跑靜態測試、Debian package resolution，再進 VM 驗收。GUI 安裝後程式碼位於 root 擁有的 `/usr/local/lib/jiukong`，一般使用者不可修改系統級檔案。沒有永久 root daemon。

建置與工具版本不混為一談：ISO 不含 AI 專有工具，工具安裝結果需要單獨的版本記錄。Codex 更新鎖檔需驗證 npm signatures、Linux 二進位啟動與 IDE。APT 金鑰輪替不直接接受新指紋，須與官方文件及公告交叉確認。

正式 Release 前依 testing.md 完成 A–Q、Intel 實機、韌體授權與來源履約檢查，將 docs/validation.md 改為實際證據；ISO、checksum、簽章、buildinfo、套件清單、繁體中文手冊一起提供。GitHub workflow 只上傳 CI artifact，不建立或發布 GitHub Release。發佈仍需專案擁有者明確授權。
