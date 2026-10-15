#!/bin/bash
# Source from user-facing installers. Privileged steps use sudo individually.
set -Eeuo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[1]}")" && pwd)
PROJECT_DIR=$(cd -- "$SCRIPT_DIR/.." && pwd)
export PROJECT_DIR SCRIPT_DIR
export PATH="$HOME/.local/bin:$PATH"
fail() { echo "錯誤：$*" >&2; exit 1; }
on_error() {
    local status=$1 line=$2
    printf '失敗：%s:%s（狀態 %s）\n' "${BASH_SOURCE[1]}" "$line" "$status" >&2
    exit "$status"
}
trap 'on_error "$?" "$LINENO"' ERR
user_system() {
    [[ $EUID != 0 ]] || fail '請以一般使用者執行；需要權限的步驟會透過 sudo 授權。'
    [[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || fail '僅支援 Linux amd64。'
    . /etc/os-release
    [[ $ID == debian && $VERSION_ID == 13 ]] || fail '請使用 Debian 13 amd64。'
    for c in sudo curl gpg dpkg apt-get python3; do command -v "$c" >/dev/null || fail "缺少 $c"; done
    [[ $(dpkg --print-architecture) == amd64 ]] || fail 'dpkg 架構不是 amd64。'
    mkdir -p "$HOME/.local/state/jiukong" "$HOME/.local/bin"
}
fetch() {
    curl --proto '=https' --proto-redir '=https' --tlsv1.2 --fail --location \
        --connect-timeout 15 --max-time 600 --retry 2 --output "$2" "$1"
}
apt_refresh() { sudo apt-get -o APT::Update::Error-Mode=any update; }
# Authenticate repository keys by primary fingerprint, then let apt verify InRelease
# and the package hashes. Refuse unreviewed replacement of existing config.
repo_install() {
    local name=$1 key_url=$2 expected=$3 uri=$4 suite=$5 package=$6
    local temp actual key dest source host
    temp=$(mktemp -d)
    fetch "$key_url" "$temp/key"
    actual=$(gpg --batch --show-keys --with-colons "$temp/key" | awk -F: '$1=="pub" {p=1} $1=="fpr" && p {print $10; p=0}')
    [[ $actual == "$expected" ]] || { rm -rf -- "$temp"; fail "$name 簽署金鑰指紋不符：$actual"; }
    gpg --batch --yes --dearmor --output "$temp/key.gpg" "$temp/key"
    key="/etc/apt/keyrings/jiukong-$name.gpg"
    dest="/etc/apt/sources.list.d/jiukong-$name.sources"
    printf 'Types: deb\nURIs: %s\nSuites: %s\nComponents: main\nArchitectures: amd64\nSigned-By: %s\n' "$uri" "$suite" "$key" > "$temp/source"
    for source in "$key" "$dest"; do
        if [[ -e $source ]]; then
            local candidate="$temp/source"
            [[ $source != "$key" ]] || candidate="$temp/key.gpg"
            cmp -s "$candidate" "$source" || { rm -rf -- "$temp"; fail "既有 $source 與預期不同；請手動檢查來源或金鑰輪替。"; }
        fi
    done
    sudo install -d -m 755 /etc/apt/keyrings
    sudo install -m 644 "$temp/key.gpg" "$key"
    sudo install -m 644 "$temp/source" "$dest"
    host=$(python3 -c 'from urllib.parse import urlparse; import sys; print(urlparse(sys.argv[1]).hostname)' "$uri")
    printf 'Package: %s\nPin: origin "%s"\nPin-Priority: 700\n\nPackage: *\nPin: origin "%s"\nPin-Priority: 1\n' "$package" "$host" "$host" > "$temp/preferences"
    sudo install -m 644 "$temp/preferences" "/etc/apt/preferences.d/jiukong-$name"
    rm -rf -- "$temp"
    apt_refresh
    apt-cache policy "$package"
    # Explicit official origin pin; no unauthenticated packages.
    sudo apt-get install "$package"
    dpkg-query -W -f='${Package} ${Version}\n' "$package" | tee -a "$HOME/.local/state/jiukong/installed.log"
}
smoke() {
    if ! timeout 30 "$@"; then
        fail "$* 無法啟動。請執行 hardware-check.py，檢查指令集、glibc 及硬體；不會以 --no-sandbox 繞過安全機制。"
    fi
}
