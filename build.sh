#!/bin/bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
fail() { echo "建置失敗：$*" >&2; exit 1; }
[[ $(uname -s) == Linux ]] || fail '需要 Debian 13 amd64 Linux 主機或 VM；macOS 無法直接執行 live-build。'
[[ $(uname -m) == x86_64 ]] || fail '需要可原生執行 amd64 的主機。'
[[ $EUID == 0 ]] || fail '請執行 sudo ./build.sh。'
. /etc/os-release
[[ $ID == debian && $VERSION_ID == 13 ]] || fail '為避免工具版本混用，請使用 Debian 13 建置。'
for c in lb debootstrap xorriso mksquashfs rsync python3 sha256sum git flock; do
    command -v "$c" >/dev/null || fail "缺少 ${c}；請依 docs/build.md 安裝建置套件。"
done
. "$ROOT/config/version.env"
export SOURCE_DATE_EPOCH
mkdir -p "$ROOT/.build" "$ROOT/logs" "$ROOT/dist"
exec 9>"$ROOT/.build/build.lock"
flock -n 9 || fail '另一個建置正在執行。'
free_kb=$(df -Pk "$ROOT/.build" | awk 'END {print $4}')
(( free_kb >= 26214400 )) || fail '至少需要 25 GiB 可用空間。'
stamp=$(date -u +%Y%m%dT%H%M%SZ)
work=$(mktemp -d "$ROOT/.build/run-$stamp-XXXXXX")
log="$ROOT/logs/build-$stamp.log"
exec > >(tee -a "$log") 2>&1
on_error() {
    local status=$1 line=$2
    printf '建置中止：行 %s，狀態 %s；工作目錄 %s；日誌 %s\n' "$line" "$status" "$work" "$log" >&2
    exit "$status"
}
trap 'on_error "$?" "$LINENO"' ERR
python3 "$ROOT/scripts/prepare-build.py" "$work"
cd "$work"
"$ROOT/scripts/configure-live.sh"
lb build
iso=live-image-amd64.hybrid.iso
[[ -s $iso ]] || fail "live-build 沒有產出 ${iso}；請查看日誌。"
out="$ROOT/dist/jiukong-$JIUKONG_VERSION-$stamp-amd64.iso"
cp -- "$iso" "$out"
cp config/jiukong-source.sha256 "$out.source.sha256"
chroot chroot dpkg-query -W -f='${binary:Package} ${Version}\n' > "$out.packages"
cp "$log" "$out.build.log"
{
    printf 'version=%s\nsuite=%s\nsource_date_epoch=%s\n' "$JIUKONG_VERSION" "$DEBIAN_SUITE" "$SOURCE_DATE_EPOCH"
    git -C "$ROOT" rev-parse --verify HEAD 2>/dev/null || echo 'git_head=uncommitted'
    dpkg-query -W live-build debootstrap xorriso squashfs-tools
} > "$out.buildinfo"
cd "$ROOT/dist"
sha256sum "$(basename "$out")" > "$(basename "$out").sha256"
echo "ISO 已建立：${out}；尚需 QEMU BIOS/UEFI 與安裝驗收。"
