"""Tests for the one-command installers."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests._loader import load

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted(p.name for p in ROOT.glob("python-*") if (p / "SKILL.md").is_file())


def run_install(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", str(ROOT / "install.sh"), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


@unittest.skipUnless(shutil.which("sh"), "sh is not available")
class ShellInstallerTest(unittest.TestCase):
    def test_help(self) -> None:
        result = run_install("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--host", result.stdout)

    def test_explicit_destination_copies_every_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            result = run_install("--dest", str(dest))
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = sorted(p.name for p in dest.iterdir() if p.is_dir())
            self.assertEqual(installed, SKILLS)
            for name in SKILLS:
                self.assertTrue((dest / name / "SKILL.md").is_file(), name)

    def test_reinstall_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            first = run_install("--dest", str(dest))
            second = run_install("--dest", str(dest))
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            installed = sorted(p.name for p in dest.iterdir() if p.is_dir())
            self.assertEqual(installed, SKILLS)

    def test_all_hosts_project_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_install("--host", "all", cwd=root)
            self.assertEqual(result.returncode, 0, result.stderr)
            for host_dir in (".agents", ".opencode", ".claude", ".codex", ".kilo", ".trae"):
                self.assertTrue(
                    (root / host_dir / "skills" / "python-coder" / "SKILL.md").is_file(),
                    host_dir,
                )

    def test_rejects_unknown_host(self) -> None:
        result = run_install("--host", "unknown")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown host", result.stderr)


class StampInstallersTest(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("stamp_installers")

    def test_stamps_both_installers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dist"
            paths = self.mod.stamp(ROOT, out, "v9.9.9")
            self.assertEqual([p.name for p in paths], ["install.sh", "install.ps1"])
            self.assertIn('REF="v9.9.9"', (out / "install.sh").read_text(encoding="utf-8"))
            self.assertIn(
                "[string]$Ref = 'v9.9.9'",
                (out / "install.ps1").read_text(encoding="utf-8"),
            )
            self.assertTrue(os.access(out / "install.sh", os.X_OK))

    def test_source_markers_are_unique(self) -> None:
        shell = (ROOT / "install.sh").read_text(encoding="utf-8")
        powershell = (ROOT / "install.ps1").read_text(encoding="utf-8")
        self.assertEqual(shell.count('REF=""'), 1)
        self.assertEqual(powershell.count("[string]$Ref = ''"), 1)

    def test_rejects_invalid_tag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                self.mod.stamp(ROOT, Path(tmp), "v1.0 beta")


@unittest.skipUnless(shutil.which("pwsh") or shutil.which("powershell"), "PowerShell is not available")
class PowerShellInstallerTest(unittest.TestCase):
    def test_script_parses(self) -> None:
        executable = shutil.which("pwsh") or shutil.which("powershell")
        assert executable is not None
        command = (
            "$tokens = $null; $errors = $null; "
            "[void][System.Management.Automation.Language.Parser]::ParseFile("
            "$env:INSTALL_PS1, [ref]$tokens, [ref]$errors); "
            "if ($errors.Count -gt 0) { $errors | ForEach-Object { Write-Error $_ }; exit 1 }"
        )
        env = os.environ.copy()
        env["INSTALL_PS1"] = str(ROOT / "install.ps1")
        result = subprocess.run(
            [executable, "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
