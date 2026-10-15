#!/usr/bin/env python3
"""Report capabilities without promising compatibility with every AI binary."""
import argparse
import json
from pathlib import Path
import platform
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "applications"))
from system_info import snapshot, command


def report():
    state = snapshot()
    cpu = state["cpu"]
    flags = set(cpu["flags"])
    checks = {
        "linux": platform.system() == "Linux",
        "amd64": platform.machine() == "x86_64",
        "long_mode": "lm" in flags,
        "sse2": "sse2" in flags,
        "intel": cpu["vendors"] == ["GenuineIntel"],
        "ram_at_least_3_5_gib": state["memory"]["total_bytes"] >= 3.5 * 1024**3,
    }
    return {"system": platform.platform(), "checks": checks,
            "isa": {f: f in flags for f in ("sse2", "ssse3", "sse4_1", "sse4_2", "popcnt", "avx", "avx2", "vmx")},
            "boot_mode": "UEFI" if Path("/sys/firmware/efi").exists() else "BIOS/unknown",
            "system_state": state,
            "pci": command(["lspci", "-nnk"]),
            "graphics": command(["glxinfo", "-B"]),
            "drm_devices": [p.name for p in Path("/sys/class/drm").glob("card*")],
            "notes": ["GPU 加速與 Intel i915/xe 相容性須以實機測試；無 AVX 不等於 Debian 無法開機。",
                      "每個第三方工具仍須執行 --version 與桌面啟動測試；不得假設支援全部 x86-64 CPU。",
                      "QEMU 的虛擬 CPU/顯示晶片不能代替 Intel iGPU 與 Wi-Fi 實測。"]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = report()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if all(result["checks"][k] for k in ("linux", "amd64", "long_mode", "sse2")) else 2)
