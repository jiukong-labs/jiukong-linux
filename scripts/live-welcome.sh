#!/bin/bash
set -Eeuo pipefail
[[ -r /run/jiukong-live-password ]] || exit 0
cat /run/jiukong-live-password
printf '\n請記下密碼。安裝到 SSD 可能格式化磁碟並刪除所有原有資料，請先備份。\n'
read -r -p '按 Enter 關閉。' _reply
