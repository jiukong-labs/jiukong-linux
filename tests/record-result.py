#!/usr/bin/env python3
"""Operator records observed manual results with required evidence."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("report", type=Path)
p.add_argument("item", choices=list("ABCDEFGHIJKLMNOPQ"))
p.add_argument("status", choices=["pass", "failed", "untested", "needs_login"])
p.add_argument("--evidence", required=True, help="觀察步驟、日誌或截圖檔名；不可只填完成")
a = p.parse_args()
d = json.loads(a.report.read_text())
if len(a.evidence.strip()) < 12:
    p.error("請提供至少 12 字的具體驗收證據")
status = a.status
if status == "pass":
    status = "simulated_pass" if d["environment"] == "qemu" else "measured_pass"
d["items"][a.item].update(status=status, evidence=a.evidence, recorded_at=datetime.now(timezone.utc).isoformat(), method="operator_observation")
a.report.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
