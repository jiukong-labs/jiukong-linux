#!/bin/bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
. "$ROOT/config/version.env"
export SOURCE_DATE_EPOCH
[[ -d config/package-lists ]] || { echo "請在 prepare-build.py 產生的工作目錄執行" >&2; exit 1; }
lb config --mode debian --distribution "$DEBIAN_SUITE" --architectures amd64 \
    --binary-images iso-hybrid --bootloaders 'syslinux grub-efi' \
    --linux-flavours amd64 --archive-areas 'main contrib non-free-firmware' \
    --apt-recommends false --apt-secure true --security true --updates true \
    --firmware-chroot true --firmware-binary true \
    --debian-installer live --debian-installer-distribution "$DEBIAN_SUITE" \
    --debian-installer-gui true --debian-installer-preseedfile config/installer.preseed \
    --mirror-bootstrap "$DEBIAN_MIRROR" --mirror-chroot "$DEBIAN_MIRROR" \
    --mirror-binary "$DEBIAN_MIRROR" --mirror-chroot-security "$DEBIAN_SECURITY_MIRROR" \
    --mirror-binary-security "$DEBIAN_SECURITY_MIRROR" \
    --bootappend-live 'boot=live components locales=zh_TW.UTF-8 keyboard-layouts=us timezone=Asia/Taipei username=jiukong hostname=jiukong zswap.enabled=0' \
    --bootappend-install 'locale=zh_TW.UTF-8 keymap=us' \
    --iso-volume JIUKONG_LIVE --iso-application "JiuKong Linux $JIUKONG_VERSION" \
    --checksums sha256 --uefi-secure-boot auto
