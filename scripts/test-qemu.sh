#!/bin/bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
if ! command -v qemu-system-x86_64 >/dev/null && command -v docker >/dev/null; then
    exec "$ROOT/scripts/test-qemu-docker.sh" "$@"
fi
fail() { echo "QEMU：$*" >&2; exit 1; }
firmware=bios
mode=live
name='test'
iso=
headless=false
while (( $# )); do
    case $1 in
        --headless) headless=true; shift;;
        --iso|--firmware|--mode|--name)
            (( $# >= 2 )) || fail "$1 缺少參數"
            case $1 in --iso) iso=$2;; --firmware) firmware=$2;; --mode) mode=$2;; --name) name=$2;; esac
            shift 2;;
        *) fail 'usage: test-qemu.sh --iso FILE --firmware bios|uefi --mode live|install|disk --name NAME';;
    esac
done
[[ $firmware == bios || $firmware == uefi ]] || fail 'firmware 必須是 bios 或 uefi'
[[ $mode == live || $mode == install || $mode == disk ]] || fail 'mode 必須是 live、install 或 disk'
[[ $name =~ ^[a-zA-Z0-9_-]+$ ]] || fail 'name 只能包含英數字、底線與連字號'
for c in qemu-system-x86_64 qemu-img python3; do command -v "$c" >/dev/null || fail "缺少 $c"; done
if [[ $mode != disk ]]; then
    [[ -f $iso ]] || fail '請以 --iso 指定既有 ISO 檔案'
    iso=$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$iso")
fi
run="$ROOT/.build/qemu/$name-$firmware"
mkdir -p "$run" "$ROOT/results"
[[ ! -L $run && ! -L $run/disk.qcow2 ]] || fail '不接受符號連結磁碟'
disk="$run/disk.qcow2"
if [[ $mode == disk ]]; then
    [[ -f $disk ]] || fail '尚無 VM 磁碟，請先執行 install 模式'
elif [[ $mode == install && ! -e $disk ]]; then
    qemu-img create -f qcow2 "$disk" 32G
fi
accel=tcg
cpu=qemu64
if [[ $(uname -s) == Linux && $(uname -m) == x86_64 && -r /dev/kvm && -w /dev/kvm ]]; then accel=kvm; cpu=host; fi
args=(-machine "q35,accel=$accel" -cpu "$cpu" -smp 2 -m 4096
      -device virtio-vga -device qemu-xhci -device usb-tablet
      -nic "user,model=virtio-net-pci" -device intel-hda -device hda-duplex
      -rtc base=utc -serial "file:$run/serial.log")
if [[ $headless == true ]]; then
    vnc_host=${JIUKONG_VNC_LISTEN:-127.0.0.1}
    [[ $vnc_host == 127.0.0.1 || $vnc_host == 0.0.0.0 ]] || fail '無效的 VNC bind 位址'
    args+=(-display none -vnc "$vnc_host:0"
           -monitor "unix:$run/monitor.sock,server=on,wait=off"
           -qmp "unix:$run/qmp.sock,server=on,wait=off")
else
    args+=(-monitor stdio)
fi
if [[ $firmware == uefi ]]; then
    code=${OVMF_CODE:-/usr/share/OVMF/OVMF_CODE_4M.fd}
    vars=${OVMF_VARS:-/usr/share/OVMF/OVMF_VARS_4M.fd}
    [[ -r $code && -r $vars ]] || fail '缺少 OVMF；macOS 可使用 OVMF_CODE/OVMF_VARS 指定韌體'
    [[ -f $run/vars.fd ]] || cp "$vars" "$run/vars.fd"
    args+=(-drive "if=pflash,format=raw,readonly=on,file=$code" -drive "if=pflash,format=raw,file=$run/vars.fd")
fi
if [[ $mode != live ]]; then
    [[ -f $disk ]] || fail 'VM 磁碟不是一般檔案'
    qemu-img info --output=json "$disk" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["format"]=="qcow2" and "backing-filename" not in d, "僅接受無 backing file 的 qcow2"'
    args+=(-drive "file=$disk,format=qcow2,if=virtio,cache=none,discard=unmap")
fi
if [[ $mode == disk ]]; then args+=(-boot order=c); else args+=(-cdrom "$iso" -boot order=d); fi
printf 'VM firmware=%s mode=%s accel=%s cpu=%s RAM=4096MiB cores=2\n' "$firmware" "$mode" "$accel" "$cpu" | tee "$run/launch.log"
echo '安裝可能刪除 VM 虛擬磁碟內所有資料；只附加專案專用 qcow2，未附加實體磁碟。'
echo 'QEMU 正常結束不代表驗收通過。請在 guest 執行 tests/guest-check.py 並記錄人工項目。'
qemu-system-x86_64 "${args[@]}"
