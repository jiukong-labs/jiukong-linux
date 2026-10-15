#!/bin/bash
set -Eeuo pipefail
[[ $EUID == 0 ]] || { echo '需要 root' >&2; exit 1; }
state=/run/jiukong-zram-device
case ${1:-} in
start)
    if [[ -r /sys/module/zswap/parameters/enabled ]] && grep -q '[Y1]' /sys/module/zswap/parameters/enabled; then
        echo 'zswap 已啟用；拒絕重疊配置。請加入 zswap.enabled=0 後重新開機。' >&2; exit 1
    fi
    [[ ! -e $state ]] || { echo '本服務已建立 zram'; exit 0; }
    modprobe zram
    dev=$(zramctl --find)
    name=${dev##*/}
    algs=$(cat "/sys/block/$name/comp_algorithm")
    alg=lzo-rle
    [[ " ${algs//[\[\]]/} " == *' lzo-rle '* ]] || alg=lzo
    [[ " ${algs//[\[\]]/} " == *" $alg "* ]] || { echo "不支援預期演算法：$algs" >&2; exit 1; }
    mem_kb=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)
    zramctl --algorithm "$alg" --size "$((mem_kb * 1024 / 2))" "$dev"
    mkswap "$dev"
    swapon --priority 100 "$dev"
    printf '%s\n' "$dev" > "$state"
    ;;
stop)
    [[ -f $state ]] || exit 0
    read -r dev < "$state"
    [[ $dev =~ ^/dev/zram[0-9]+$ ]] || exit 1
    swapoff "$dev"
    zramctl --reset "$dev"
    rm -- "$state"
    ;;
*) echo 'usage: zram.sh start|stop' >&2; exit 2;;
esac
