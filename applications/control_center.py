#!/usr/bin/env python3
"""JiuKong Control Center: unprivileged Tk GUI, no resident privileged helper."""
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from system_info import snapshot, tool_versions, cpu_sample, cpu_usage, read_text

ROOT = Path(__file__).resolve().parent.parent


def mib(value):
    return "未知" if value is None else f"{value / 1024**2:.0f} MiB"


class Center:
    def __init__(self, window):
        self.window = window
        window.title("JiuKong Control Center — 久空系統控制中心")
        window.geometry("780x650")
        self.queue = queue.Queue()
        self.busy = False
        self.previous_cpu = None
        self.versions = "版本狀態尚未讀取"
        outer = ttk.Frame(window, padding=14)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="久空 AI 開發工作站", font=("sans", 18)).pack(anchor="w")
        navigation = ttk.Frame(outer)
        navigation.pack(fill="x", pady=(8, 0))
        ttk.Button(navigation, text="應用程式（已安裝程式）",
                   command=lambda: self.launch(["xfce4-appfinder"])).pack(side="left", padx=2)
        ttk.Button(navigation, text="Firefox 瀏覽器",
                   command=lambda: self.launch(["firefox-esr"])).pack(side="left", padx=2)
        ttk.Button(navigation, text="藍牙設備",
                   command=lambda: self.launch(["blueman-manager"])).pack(side="left", padx=2)
        self.state_text = tk.Text(outer, height=23, wrap="word", state="disabled")
        self.state_text.pack(fill="both", expand=True, pady=10)
        tools = ttk.Frame(outer)
        tools.pack(fill="x")
        for i, (label, name) in enumerate((("VS Code", "vscode"), ("Codex CLI", "codex"),
                                            ("Claude Code", "claude-code"), ("ChatGPT", "chatgpt"),
                                            ("Claude Desktop", "claude-desktop"))):
            ttk.Button(tools, text=f"安裝／更新 {label}", command=lambda n=name: self.script(f"install-{n}.sh")).grid(row=i // 2, column=i % 2, sticky="ew", padx=3, pady=3)
        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=8)
        for label, args in (("開啟 VS Code", ["code"]), ("開啟 ChatGPT", ["chatgpt"]),
                            ("開啟 Claude", ["claude-desktop"]), ("終端機", ["xfce4-terminal"]),
                            ("鎖定", ["light-locker-command", "--lock"])):
            ttk.Button(actions, text=label, command=lambda a=args: self.launch(a)).pack(side="left", padx=2)
        ttk.Button(outer, text="系統更新（終端機內 sudo 授權）", command=lambda: self.script("update-system.sh")).pack(anchor="w")
        ttk.Button(outer, text="重新讀取工具版本", command=lambda: self.refresh(True)).pack(anchor="w", pady=4)
        ttk.Label(outer, text="工具安裝與授權在終端機進行；版本存在不代表登入或擴充套件載入已通過。", wraplength=740).pack(anchor="w")
        self.refresh(True)
        window.after(100, self.drain)
        window.after(5000, self.tick)

    def launch(self, args):
        if not shutil.which(args[0]):
            messagebox.showerror("無法開啟", f"找不到 {args[0]}，請先安裝。")
            return
        try:
            subprocess.Popen(args, start_new_session=True)
        except OSError as e:
            messagebox.showerror("無法開啟", str(e))

    def script(self, name):
        self.launch(["xfce4-terminal", "--hold", "--execute", str(ROOT / "scripts" / name)])

    def refresh(self, versions=False):
        if self.busy:
            return
        self.busy = True
        def worker():
            try:
                state = snapshot()
                sample = cpu_sample(read_text("/proc/stat"))
                versions_result = tool_versions() if versions else None
                self.queue.put((state, sample, versions_result, None))
            except Exception as e:
                self.queue.put((None, None, None, str(e)))
        threading.Thread(target=worker, daemon=True).start()

    def tick(self):
        self.refresh()
        self.window.after(5000, self.tick)

    def drain(self):
        try:
            state, sample, versions, error = self.queue.get_nowait()
        except queue.Empty:
            pass
        else:
            self.busy = False
            if error:
                self.render("讀取系統狀態失敗：" + error)
            else:
                usage = "取樣中" if self.previous_cpu is None else f"{cpu_usage(self.previous_cpu, sample):.1f}%"
                self.previous_cpu = sample
                if versions is not None:
                    self.versions = "\n".join(f"{k}: [{v['status']}] {v['output']}" for k, v in versions.items())
                m, d = state["memory"], state["disk"]
                self.render(f"CPU: {', '.join(state['cpu']['models'])}\nCPU 使用率: {usage}\n"
                            f"實體 RAM: {mib(m['total_bytes'])}　可用: {mib(m['available_bytes'])}　使用: {mib(m['used_bytes'])}\n"
                            f"根目錄容量: {d['total_bytes'] / 1024**3:.1f} GiB　可用: {d['free_bytes'] / 1024**3:.1f} GiB\n"
                            f"網路: {state['network']['output']}\n"
                            f"swappiness: {state['swappiness']}　zswap: {state['zswap_enabled']}\n\n"
                            f"zram:\n{state['zram']['output']}\nSwap:\n{state['swap']['output']}\n\n"
                            f"工具版本（僅安裝／啟動檢查）:\n{self.versions}\n\n磁碟（ROTA=false/0 表示非旋轉媒體）:\n{state['block_devices']['output']}")
        self.window.after(100, self.drain)

    def render(self, text):
        self.state_text.configure(state="normal")
        self.state_text.delete("1.0", "end")
        self.state_text.insert("end", text)
        self.state_text.configure(state="disabled")


if __name__ == "__main__":
    if os.geteuid() == 0:
        sys.exit("控制中心不得以 root 執行，請使用一般桌面帳號。")
    window = tk.Tk()
    Center(window)
    window.mainloop()
