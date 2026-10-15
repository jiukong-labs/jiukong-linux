#!/bin/bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
# Broader mount/device permissions are restricted to disposable hosted runners.
container_permissions=(--cap-add SYS_ADMIN)
case ${1:-} in
    '') ;;
    --github-hosted)
        [[ ${GITHUB_ACTIONS:-} == true && ${RUNNER_ENVIRONMENT:-} == github-hosted && $(uname -s) == Linux && $(uname -m) == x86_64 ]] || {
            echo '--github-hosted 僅限 GitHub 一次性 Linux x64 runner' >&2
            exit 1
        }
        container_permissions=(--privileged)
        ;;
    *) echo "未知選項：$1" >&2; exit 1 ;;
esac
command -v docker >/dev/null || { echo '找不到 Docker CLI' >&2; exit 1; }
free_kb=$(df -Pk "$ROOT" | awk 'END {print $4}')
(( free_kb >= 26214400 )) || { echo '主機至少需要 25 GiB 可用空間' >&2; exit 1; }
mkdir -p "$ROOT/logs" "$ROOT/dist"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
exec > >(tee "$ROOT/logs/docker-build-$stamp.log") 2>&1
python3 "$ROOT/scripts/lib/docker-health.py"
docker build --platform linux/amd64 --target check-base -f "$ROOT/tests/docker/Dockerfile" -t jiukong-linux-check-base:debian13-amd64 "$ROOT"
docker build --platform linux/amd64 -f "$ROOT/tests/docker/Dockerfile.build" -t jiukong-linux-builder:debian13-amd64 "$ROOT"
name="jiukong-build-$stamp"
# Default SYS_ADMIN alone may be insufficient under Docker mount restrictions.
# Hosted mode permits live-build mounts only inside the disposable cloud VM.
# No host directory or Docker socket is mounted in either mode.
docker create --platform linux/amd64 "${container_permissions[@]}" --name "$name" \
    jiukong-linux-builder:debian13-amd64
echo "建置容器：${name}；失敗時保留供除錯。"
if docker start -a "$name"; then
    status=$(docker inspect --format '{{.State.ExitCode}}' "$name")
else
    status=$(docker inspect --format '{{.State.ExitCode}}' "$name")
    [[ $status != 0 ]] || status=1
fi
if [[ $status != 0 ]]; then
    echo "建置失敗（${status}）；容器 $name 保留，日誌可用 docker logs $name 查看。" >&2
    exit "$status"
fi
docker cp "$name:/work/dist/." "$ROOT/dist/"
docker cp "$name:/work/logs/." "$ROOT/logs/"
(cd "$ROOT/dist" && sha256sum -c ./*.iso.sha256) 2>/dev/null || \
    (cd "$ROOT/dist" && shasum -a 256 -c ./*.iso.sha256)
docker rm "$name"
echo 'ISO 已複製到 dist/；尚需 BIOS/UEFI 與安裝驗收。'
