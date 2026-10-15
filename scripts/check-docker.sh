#!/bin/bash
set -Eeuo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
command -v docker >/dev/null || { echo '找不到 Docker CLI' >&2; exit 1; }
mkdir -p "$ROOT/logs"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
exec > >(tee "$ROOT/logs/docker-check-$stamp.log") 2>&1
python3 "$ROOT/scripts/lib/docker-health.py"
tag=jiukong-linux-check:debian13-amd64
docker build --platform linux/amd64 -f "$ROOT/tests/docker/Dockerfile" -t "$tag" "$ROOT"
docker image inspect --format '{{.Id}} {{.Os}}/{{.Architecture}}' "$tag"
# Source is copied into the image. No host mounts, privileged mode or Docker socket.
docker run --rm --platform linux/amd64 "$tag"
