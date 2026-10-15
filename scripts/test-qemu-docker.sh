#!/bin/bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
fail() { echo "Docker QEMU：$*" >&2; exit 1; }
mode=live
firmware=bios
name='test'
iso=
while (( $# )); do
    case $1 in
        --headless) shift;;
        --iso|--firmware|--mode|--name)
            (( $# >= 2 )) || fail "$1 缺少參數"
            case $1 in --iso) iso=$2;; --firmware) firmware=$2;; --mode) mode=$2;; --name) name=$2;; esac
            shift 2;;
        *) fail "無效參數：$1";;
    esac
done
[[ $mode == live || $mode == install || $mode == disk ]] || fail 'mode 必須是 live/install/disk'
[[ $firmware == bios || $firmware == uefi ]] || fail 'firmware 必須是 bios/uefi'
[[ $name =~ ^[a-zA-Z0-9_-]+$ ]] || fail 'name 只能包含英數字、底線與連字號'
[[ $mode == disk || -f $iso ]] || fail '請以 --iso 指定 ISO 檔案'
command -v docker >/dev/null || fail '找不到 Docker'
python3 "$ROOT/scripts/lib/docker-health.py"
tag=jiukong-linux-qemu:debian13
# Use the daemon's native CPU for QEMU itself; the guest is always x86-64.
docker build -f "$ROOT/tests/docker/Dockerfile.qemu" -t "$tag" "$ROOT"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
container="jiukong-qemu-$name-$firmware-$stamp"
volume="jiukong-qemu-$name-$firmware"
args=(--firmware "$firmware" --mode "$mode" --name "$name" --headless)
[[ $mode == disk ]] || args+=(--iso /work/dist/test.iso)
docker create --name "$container" --publish 127.0.0.1::5900 \
    --mount "type=volume,src=$volume,dst=/work/.build/qemu" \
    "$tag" bash scripts/test-qemu.sh "${args[@]}"
if [[ $mode != disk ]]; then docker cp "$iso" "$container:/work/dist/test.iso"; fi
docker start "$container"
sleep 2
[[ $(docker inspect --format '{{.State.Running}}' "$container") == true ]] || {
    docker logs "$container"
    fail "VM 未能持續執行；保留容器 $container 供除錯"
}
echo "QEMU 已啟動（不代表開機驗收成功）：$container"
docker port "$container" 5900/tcp
echo "可用 macOS 螢幕共享連到以上 localhost VNC 位址；停止：docker stop $container"
echo "虛擬磁碟保存在專案專用 Docker volume：$volume"
