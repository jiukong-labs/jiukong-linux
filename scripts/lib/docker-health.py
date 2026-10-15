#!/usr/bin/env python3
"""Bound Docker preflight so a stalled engine cannot hang task scripts forever."""
import subprocess
import sys

try:
    subprocess.run(
        ["docker", "info", "--format",
         "{{.OperatingSystem}}/{{.Architecture}} memory={{.MemTotal}} cpus={{.NCPU}}"],
        check=True,
        timeout=20,
    )
except (OSError, subprocess.SubprocessError) as error:
    sys.exit(f"Docker 引擎無法正常回應：{error}")
