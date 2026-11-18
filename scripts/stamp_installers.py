#!/usr/bin/env python3
"""Stamp the installers with a release tag.

Release assets should install the release they were downloaded from, not whatever
is latest at install time. This replaces the empty default ref in ``install.sh``
and ``install.ps1`` with the tag, copies them to ``--out``, and marks the shell
installer executable.

Usage:
    python3 scripts/stamp_installers.py v0.1.5 --out dist

Dependency-free. Run from the repository root.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHELL_MARKER = 'REF=""'
POWERSHELL_MARKER = "[string]$Ref = ''"


def replace_once(text: str, old: str, new: str, path: Path) -> str:
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{path}: expected exactly one {old!r}, found {count}")
    return text.replace(old, new, 1)


def stamp(root: Path, out_dir: Path, tag: str) -> list[Path]:
    if not tag or any(ch.isspace() for ch in tag):
        raise ValueError(f"invalid release tag: {tag!r}")

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    shell_source = root / "install.sh"
    shell_target = out_dir / "install.sh"
    shell_text = replace_once(
        shell_source.read_text(encoding="utf-8"),
        SHELL_MARKER,
        f'REF="{tag}"',
        shell_source,
    )
    shell_target.write_text(shell_text, encoding="utf-8")
    os.chmod(shell_target, 0o755)
    written.append(shell_target)

    powershell_source = root / "install.ps1"
    powershell_target = out_dir / "install.ps1"
    powershell_text = replace_once(
        powershell_source.read_text(encoding="utf-8"),
        POWERSHELL_MARKER,
        f"[string]$Ref = '{tag}'",
        powershell_source,
    )
    powershell_target.write_text(powershell_text, encoding="utf-8")
    written.append(powershell_target)

    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stamp installers with a release tag.")
    parser.add_argument("tag", help="Release tag, for example v0.1.5")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root")
    parser.add_argument("--out", type=Path, default=Path("dist"), help="Output directory")
    args = parser.parse_args(argv)

    try:
        paths = stamp(args.root, args.out, args.tag)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for path in paths:
        print(f"wrote: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
