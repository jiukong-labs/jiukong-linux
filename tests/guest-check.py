#!/usr/bin/env python3
"""Collect evidence inside a guest; never convert untested manual items to passes."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "applications"))
from system_info import snapshot, command, tool_versions

ITEMS = dict(zip("ABCDEFGHIJKLMNOPQ", [
    "系統開機", "Openbox 桌面登入", "網路連線", "閒置 RAM", "VS Code 視窗啟動",
    "Codex 擴充套件載入", "Claude Code 擴充套件載入", "Codex CLI 啟動", "Claude Code CLI 啟動",
    "ChatGPT Desktop 啟動", "Claude Desktop 啟動", "中文輸入", "zram 與磁碟 swap",
    "安全更新", "Live ISO 開機", "虛擬磁碟安裝完成", "安裝後重新開機登入"]))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--environment", choices=["qemu", "hardware"], required=True)
    p.add_argument("--idle", action="store_true", help="操作者確認登入後已閒置五分鐘且未開啟工具")
    p.add_argument("--output", default="results/acceptance.json")
    args = p.parse_args()
    if platform.system() != "Linux":
        sys.exit("此測試必須在 Linux guest 或實機執行")
    state = snapshot()
    tools = tool_versions()
    items = {k: {"name": v, "status": "untested", "evidence": "需要人工驗收，參考 docs/testing.md"} for k, v in ITEMS.items()}
    def record(key, passed, evidence):
        items[key].update(status=("simulated_pass" if args.environment == "qemu" else "measured_pass") if passed else "failed", evidence=evidence)
    boot = command(["systemctl", "is-system-running"])
    record("A", boot.get("output") == "running", boot)
    network = command(["curl", "--proto", "=https", "-fsSI", "--connect-timeout", "10", "--max-time", "20", "https://deb.debian.org/debian/README"])
    record("C", network["status"] == "ok", network)
    if args.idle:
        used = state["memory"]["used_bytes"]
        items["D"].update(status="simulated_measurement" if args.environment == "qemu" else "measured", evidence={"used_bytes": used, "definition": "MemTotal - MemAvailable", "target_300_550_mib": used is not None and 300 * 1024**2 <= used <= 550 * 1024**2})
    for key, tool in (("H", "codex"), ("I", "claude")):
        record(key, tools[tool]["status"] == "ok", tools[tool])
    swap = command(["swapon", "--show", "--json", "--bytes"])
    try:
        devices = json.loads(swap["output"])["swapdevices"]
        active_zram = any(str(d["name"]).startswith("/dev/zram") and d["size"] > 0 for d in devices)
        active_disk = any(not str(d["name"]).startswith("/dev/zram") and d["size"] > 0 for d in devices)
        if active_zram and active_disk:
            items["M"].update(status="needs_pressure_test", evidence=devices)
        else:
            items["M"].update(status="partial" if active_zram else "failed", evidence={"active_zram": active_zram, "active_disk_swap": active_disk, "note": "Live 預設不建立磁碟 swap；運作仍需壓力測試。"})
    except (ValueError, KeyError, TypeError):
        items["M"].update(status="failed", evidence=swap)
    for key in ("F", "G", "J", "K"):
        items[key]["login_followup"] = "需要使用者登入後進行實機測試"
    result = {"timestamp": datetime.now(timezone.utc).isoformat(), "environment": args.environment,
              "items": items, "system": state, "tool_versions": tools,
              "desktop_process": command(["pgrep", "-a", "openbox"]),
              "vscode_extensions": command(["code", "--list-extensions", "--show-versions"])}
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(target)
    sys.exit(1 if any(i["status"] == "failed" for i in items.values()) else 0)
