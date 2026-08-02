#!/usr/bin/env python3
"""Sync the bundled ``pyast_utils`` fallback copies across the skills.

The shared filesystem/AST helpers live once at
``python-dependency-analyzer/scripts/pyast_utils.py``. Skills whose scripts import
the module ship a byte-identical copy in their own ``scripts/`` so the skill still
works when copied out of the suite and installed standalone.

This script is the way those copies are produced: it copies the canonical module
to every skill that needs a fallback. Do not hand-edit a fallback; regenerate with
this tool instead. ``scripts/validate_suite.py`` checks that every fallback matches
the canonical file (as ``--check`` does here), so drift is caught either way.

Dependency-free. Run from the repository root:

    python3 scripts/sync_pyast_utils.py          # copy canonical -> every needing skill
    python3 scripts/sync_pyast_utils.py --check  # verify only; non-zero exit on drift
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CANONICAL_REL = "python-dependency-analyzer/scripts/pyast_utils.py"
SKILL_SCRIPTS_REL = "python-*/scripts"


def canonical_path(root: Path = ROOT) -> Path:
    return root / CANONICAL_REL


def target_dirs(root: Path = ROOT) -> list[Path]:
    """Return the ``scripts/`` dirs of skills that need a bundled fallback."""
    canonical = canonical_path(root).resolve()
    targets: set[Path] = set()
    for skill_scripts in sorted(root.glob(SKILL_SCRIPTS_REL)):
        if skill_scripts.resolve() == canonical.parent.resolve():
            continue
        for script in skill_scripts.glob("*.py"):
            if "pyast_utils" in script.read_text(encoding="utf-8"):
                targets.add(skill_scripts)
                break
    return sorted(targets)


def sync(root: Path = ROOT, check: bool = False) -> list[str]:
    canonical = canonical_path(root)
    if not canonical.exists():
        print(f"error: canonical shared module not found: {canonical}", file=sys.stderr)
        return ["canonical-missing"]

    canonical_bytes = canonical.read_bytes()
    problems: list[str] = []
    for scripts_dir in target_dirs(root):
        skill = scripts_dir.parent.name
        bundled = scripts_dir / "pyast_utils.py"
        if not bundled.exists():
            problems.append(f"{skill}: missing bundled pyast_utils.py")
            continue
        if bundled.read_bytes() != canonical_bytes:
            problems.append(f"{skill}: bundled pyast_utils.py does not match canonical")

    if check:
        if problems:
            for msg in problems:
                print(f"drift: {msg}", file=sys.stderr)
            return problems
        print("pyast_utils fallbacks: all in sync")
        return []

    if problems:
        for msg in problems:
            print(f"will fix: {msg}")
    written = 0
    for scripts_dir in target_dirs(root):
        bundled = scripts_dir / "pyast_utils.py"
        if bundled.exists() and bundled.read_bytes() == canonical_bytes:
            continue
        bundled.write_bytes(canonical_bytes)
        written += 1
        print(f"wrote: {bundled}")
    if written == 0:
        print("pyast_utils fallbacks: up to date")
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync bundled pyast_utils fallback copies.")
    parser.add_argument("--check", action="store_true", help="Verify copies only; do not write.")
    args = parser.parse_args()

    problems = sync(check=args.check)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())