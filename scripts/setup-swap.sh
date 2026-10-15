#!/bin/bash
set -Eeuo pipefail
[[ $EUID == 0 ]] || { echo '需要 sudo' >&2; exit 1; }
[[ ! -d /run/live/medium ]] || { echo 'Live 模式不建立 SSD swapfile'; exit 0; }
exec 9>/run/lock/jiukong-swap.lock
flock -n 9 || exit 1
# Existing disk swap chosen by the installer takes precedence.
if swapon --noheadings --show=NAME | grep -qv '/dev/zram'; then
    echo '已有磁碟 swap；保留既有設定。'; exit 0
fi
if [[ -e /swapfile || -L /swapfile ]]; then
    # Only activate a previously configured swapfile; never overwrite it.
    grep -Eq '^/swapfile[[:space:]]+none[[:space:]]+swap[[:space:]]' /etc/fstab || {
        echo '/swapfile 已存在且未設定，拒絕覆寫。' >&2; exit 1;
    }
    swapon /swapfile
    exit 0
fi
[[ $(findmnt -n -o FSTYPE /) == ext4 ]] || { echo '自動 swapfile 僅支援 ext4；請依 docs/memory.md 手動配置。' >&2; exit 1; }
free_kb=$(df -Pk / | awk 'END {print $4}')
(( free_kb >= 4194304 )) || { echo '至少需剩餘 4 GiB 才能建立 2 GiB swapfile' >&2; exit 1; }
umask 077
# noclobber prevents replacing a pre-existing path.
(set -C; : > /swapfile)
chmod 600 /swapfile
dd if=/dev/zero of=/swapfile bs=1M count=2048 conv=fsync status=progress
mkswap /swapfile
swapon --priority 10 /swapfile
printf '/swapfile none swap sw,pri=10 0 0\n' >> /etc/fstab
