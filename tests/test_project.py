import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "applications"))
from system_info import parse_meminfo, parse_cpuinfo, cpu_sample, cpu_usage, command


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProbeTests(unittest.TestCase):
    def test_available_memory_accounts_for_reclaimable_cache(self):
        m = parse_meminfo("MemTotal: 4000 kB\nMemFree: 100 kB\nMemAvailable: 3000 kB\n")
        self.assertEqual(m["MemTotal"] - m["MemAvailable"], 1024000)
        self.assertNotEqual(m["MemTotal"] - m["MemFree"], 1024000)

    def test_unknown_available_not_misreported(self):
        self.assertNotIn("MemAvailable", parse_meminfo("MemTotal: 4000 kB\n"))

    def test_cpu_flags_use_intersection(self):
        text = "processor : 0\nvendor_id : GenuineIntel\nmodel name : Old Intel\nflags : lm sse2 avx\n\nprocessor : 1\nvendor_id : GenuineIntel\nmodel name : Old Intel\nflags : lm sse2\n"
        cpu = parse_cpuinfo(text)
        self.assertEqual(cpu["logical_cpus"], 2)
        self.assertEqual(cpu["flags"], ["lm", "sse2"])
        self.assertEqual(cpu["vendors"], ["GenuineIntel"])

    def test_cpu_guest_ticks_not_double_counted(self):
        self.assertEqual(cpu_sample("cpu 10 0 5 100 5 0 0 0 10 0\n"), (120, 105))
        self.assertEqual(cpu_usage((100, 90), (200, 140)), 50)
        self.assertEqual(cpu_usage((100, 90), (100, 90)), 0)

    def test_missing_program_is_unavailable(self):
        self.assertEqual(command(["/definitely/not/a/program"])["status"], "unavailable")

    def test_failed_command_not_success(self):
        self.assertEqual(command([sys.executable, "-c", "raise SystemExit(2)"])["status"], "failed")


class ProjectTests(unittest.TestCase):
    def test_jsonc_and_locale_settings_preserved(self):
        config = load("vscode_config", "scripts/configure-vscode.py")
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / ".config/Code/User"
            folder.mkdir(parents=True)
            existing = '{ // user comment\n "editor.fontSize": 18,\n}\n'
            (folder / "settings.json").write_text(existing)
            config.configure(temp)
            self.assertEqual((folder / "settings.json").read_text(), existing)
            self.assertTrue(json.loads((folder / "jiukong-settings.json").read_text())["security.workspace.trust.enabled"])

    def test_first_install_uses_secure_defaults(self):
        config = load("vscode_first", "scripts/configure-vscode.py")
        with tempfile.TemporaryDirectory() as temp:
            config.configure(temp)
            settings = json.loads((Path(temp) / ".config/Code/User/settings.json").read_text())
            self.assertTrue(settings["git.enabled"])
            self.assertEqual(settings["files.autoSave"], "afterDelay")
            self.assertTrue(settings["security.workspace.trust.enabled"])

    def test_stage_contains_boot_and_installed_contracts(self):
        stage = load("stage", "scripts/prepare-build.py")
        with tempfile.TemporaryDirectory() as temp:
            work = Path(temp) / "fresh"
            stage.prepare(work)
            image = work / "config/includes.chroot"
            self.assertTrue((image / "usr/local/lib/jiukong/scripts/install-all.sh").stat().st_mode & 0o111)
            self.assertTrue((image / "usr/lib/live/config/9991-jiukong-password").exists())
            self.assertIn("zswap.enabled=0", (image / "etc/default/grub.d/jiukong.cfg").read_text())
            self.assertTrue((image / "usr/share/jiukong/source.sha256").is_file())
            self.assertTrue((image / "usr/local/lib/jiukong/config/codex/package-lock.json").exists())
            self.assertTrue((image / "etc/skel/.config/openbox/autostart").is_file())
            self.assertTrue((image / "usr/share/applications/jiukong-control-center.desktop").is_file())
            with self.assertRaises(ValueError):
                stage.prepare(work)

    def test_debian_installer_requires_manual_partitioning(self):
        entries = [l for l in (ROOT / "config/installer.preseed").read_text().splitlines() if l and not l.startswith("#")]
        self.assertFalse(any("partman" in l or "password-crypted" in l or "late_command" in l for l in entries))

    def test_codex_locked_https_integrity_for_linux_x64(self):
        lock = json.loads((ROOT / "config/codex/package-lock.json").read_text())
        packages = lock["packages"]
        self.assertIn("node_modules/@openai/codex-linux-x64", packages)
        for name, entry in packages.items():
            if name:
                self.assertTrue(entry["resolved"].startswith("https://registry.npmjs.org/"))
                self.assertTrue(entry["integrity"].startswith("sha512-"))

    def test_shell_and_xml_syntax(self):
        files = [ROOT / "build.sh", *ROOT.glob("scripts/**/*.sh"), *ROOT.glob("config/hooks/**/*.chroot"), *ROOT.glob("config/includes.chroot/usr/lib/live/config/*")]
        for f in files:
            with self.subTest(file=str(f.relative_to(ROOT))):
                subprocess.run(["bash", "-n", str(f)], check=True, capture_output=True)
        for path in (ROOT / "desktop/openbox").glob("*.xml"):
            ET.parse(path)

    def test_build_rejects_unsupported_host_before_mutation(self):
        if sys.platform == "darwin":
            p = subprocess.run([str(ROOT / "build.sh")], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("Debian 13", p.stderr)


if __name__ == "__main__":
    unittest.main()
