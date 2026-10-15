#!/usr/bin/env python3
"""Bounded benchmark. Only writes its own temporary regular file."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import sys
import tempfile
import time
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "applications"))
from system_info import snapshot, read_text


def benchmark(directory, seconds, pressure_mib):
    before = snapshot()
    block = b"j" * (1024 * 1024)
    start = time.monotonic()
    rounds = 0
    while time.monotonic() - start < seconds:
        hashlib.sha256(block).digest()
        rounds += 1
    elapsed = time.monotonic() - start
    # 128 MiB memory copy, representative only; never infer available capacity.
    memory = bytearray(128 * 1024**2)
    t = time.monotonic()
    copy = memory[:]
    memory_seconds = time.monotonic() - t
    del copy, memory
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    if os.statvfs(directory).f_bavail * os.statvfs(directory).f_frsize < 512 * 1024**2:
        raise RuntimeError("磁碟測試至少需要 512 MiB 可用空間")
    with tempfile.TemporaryFile(dir=directory) as f:
        t = time.monotonic()
        for _ in range(128):
            f.write(block)
        f.flush()
        os.fsync(f.fileno())
        write_seconds = time.monotonic() - t
        f.seek(0)
        t = time.monotonic()
        while f.read(1024**2):
            pass
        read_seconds = time.monotonic() - t
    pressure = None
    if pressure_mib:
        t = time.monotonic()
        pages = []
        for _ in range(pressure_mib):
            # Touch incompressible data; keep kernel OOM and earlyoom enabled.
            pages.append(os.urandom(1024**2))
        during = snapshot()
        time.sleep(seconds)
        pressure = {"allocated_mib": pressure_mib, "held_seconds": seconds,
                    "elapsed_seconds": time.monotonic() - t, "during": during,
                    "vmstat": read_text("/proc/vmstat"), "psi_memory": read_text("/proc/pressure/memory")}
        del pages
    return {"timestamp": datetime.now(timezone.utc).isoformat(), "platform": platform.platform(),
            "measurement_environment": "operator_must_identify_qemu_or_hardware",
            "cpu_sha256_mib_s": rounds / elapsed, "memory_copy_128mib_seconds": memory_seconds,
            "disk_write_128mib_fsync_seconds": write_seconds,
            "disk_read_128mib_cached_seconds": read_seconds,
            "disk_test_directory": str(directory),
            "disk_limitations": "非 O_DIRECT；讀取可能命中 page cache，不代表 SSD 原始速度。Live overlay 測試不代表 SSD。",
            "before": before, "after": snapshot(), "pressure": pressure,
            "max_rss_platform_units": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--directory", default=".")
    p.add_argument("--seconds", type=int, default=3, choices=range(1, 31))
    p.add_argument("--pressure-mib", type=int, default=0, choices=range(0, 3073), help="顯式啟用最多 3072 MiB 壓力；可能觸發 OOM 終止測試")
    p.add_argument("--output", default="results/benchmark.json")
    args = p.parse_args()
    result = benchmark(args.directory, args.seconds, args.pressure_mib)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(output)
