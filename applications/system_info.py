"""Read-only Linux system probes, shared by GUI, hardware and acceptance tools."""
from pathlib import Path
import json
import os
import platform
import shutil
import subprocess


def command(args, timeout=5):
    # Emulated runtimes can return 127 instead of propagating ENOENT to Python.
    # Resolve the executable first so missing tools have a consistent status.
    if not shutil.which(args[0]):
        return {"status": "unavailable", "output": f"找不到命令：{args[0]}"}
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
        return {"status": "ok" if p.returncode == 0 else "failed", "code": p.returncode,
                "output": (p.stdout + p.stderr).strip()[:12000]}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {"status": "unavailable", "output": str(e)}


def parse_meminfo(text):
    values = {}
    for line in text.splitlines():
        key, _, value = line.partition(":")
        if value.split() and value.split()[0].isdigit():
            values[key] = int(value.split()[0]) * 1024
    return values


def parse_cpuinfo(text):
    # Intersect flags across processors. Do not infer ISA support from model names.
    sections = [s for s in text.strip().split("\n\n") if s.strip()]
    models, vendors, flags = [], [], []
    for section in sections:
        entries = dict((k.strip(), v.strip()) for k, _, v in
                       (line.partition(":") for line in section.splitlines() if ":" in line))
        models.append(entries.get("model name", "unknown"))
        vendors.append(entries.get("vendor_id", "unknown"))
        flags.append(set(entries.get("flags", "").split()))
    common = set.intersection(*flags) if flags else set()
    return {"models": sorted(set(models)), "vendors": sorted(set(vendors)),
            "logical_cpus": len(sections), "flags": sorted(common)}


def cpu_sample(text):
    values = [int(v) for v in text.splitlines()[0].split()[1:9]]
    return sum(values), values[3] + (values[4] if len(values) > 4 else 0)


def cpu_usage(previous, current):
    total = current[0] - previous[0]
    if total <= 0:
        return 0.0
    return max(0.0, min(100.0, 100 * (1 - (current[1] - previous[1]) / total)))


def read_text(path):
    try:
        return Path(path).read_text()
    except OSError:
        return ""


def snapshot():
    memory = parse_meminfo(read_text("/proc/meminfo"))
    total = memory.get("MemTotal", 0)
    available = memory.get("MemAvailable")
    disk = shutil.disk_usage("/")
    return {
        "cpu": parse_cpuinfo(read_text("/proc/cpuinfo")),
        "memory": {"total_bytes": total, "available_bytes": available,
                   "used_bytes": total - available if available is not None else None},
        "disk": {"total_bytes": disk.total, "free_bytes": disk.free},
        "zram": command(["zramctl", "--output", "NAME,ALGORITHM,DISKSIZE,DATA,COMPR,TOTAL"]),
        "swap": command(["swapon", "--show", "--bytes"]),
        "network": command(["nmcli", "-t", "-f", "STATE,CONNECTIVITY", "general"]),
        "block_devices": command(["lsblk", "-J", "-o", "NAME,TYPE,SIZE,ROTA,MODEL,MOUNTPOINTS"]),
        "swappiness": read_text("/proc/sys/vm/swappiness").strip(),
        "zswap_enabled": read_text("/sys/module/zswap/parameters/enabled").strip(),
    }


def tool_versions():
    results = {}
    for tool in ("code", "codex", "claude", "chatgpt", "claude-desktop"):
        path = shutil.which(tool)
        if not path:
            results[tool] = {"status": "not_installed", "output": "未安裝"}
        elif tool in {"chatgpt", "claude-desktop"}:
            # Avoid accidentally launching a GUI during a status refresh.
            results[tool] = command(["dpkg-query", "-W", "-f=${Version}", tool])
        else:
            results[tool] = command([path, "--version"], timeout=15)
    return results
