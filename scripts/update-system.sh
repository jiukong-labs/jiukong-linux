#!/bin/bash
set -Eeuo pipefail
. "$(dirname -- "${BASH_SOURCE[0]}")/lib/common.sh"
user_system
apt_refresh
# Keep apt's confirmation prompt; no automatic removals or reboot.
sudo apt-get upgrade
if [[ -f /var/run/reboot-required ]]; then echo '更新完成；請儲存工作後重新開機。'; fi
echo 'Debian 與已啟用的官方 apt 工具來源已更新；Codex npm 鎖更新方式見 docs/tools.md。'
