#!/usr/bin/env python3
"""Enforce a layer-rule contract over a Python repository's imports.

CI-gateable and dependency-free. Reads a JSON layer contract and reports every
first-party import that violates a forbidden from-layer -> to-layer rule.
Exit code 0 = clean, 1 = violations found, 2 = usage/config error.
Filesystem and AST helpers are imported from the shared ``pyast_utils`` module
in ``python-dependency-analyzer/scripts`` (see that module). The import
resolves the canonical suite copy when the suite is installed as a whole and
falls back to a bundled copy shipped in this skill so the script also works
when the skill is installed standalone.

Contract example (JSON):

    {
      "layers": {
        "domain": ["app/domain"],
        "application": ["app/application"],
        "infrastructure": ["app/infrastructure"],
        "handlers": ["app/handlers"]
      },
      "forbidden": [
        {"from": "domain", "to": ["infrastructure", "handlers", "web", "orm"]}
      ]
    }

A ``to`` entry matches a target by its layer name, by its top-level module name,
or by a built-in keyword category (``web``, ``orm``, ``queue``, ``cache``,
``http_client``, ``storage``). Type-only imports are treated as imports; use
``--exclude`` for intentional exceptions.

Usage:
    python3 check_layer_rules.py --config contract.json [root]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _pyast_utils_scripts_dir() -> Path | None:
    """Locate the directory holding the shared ``pyast_utils`` module.

    Resolution order:
    1. The canonical suite copy, found by walking up from this script so a
       whole-suite install works at any location and depth.
    2. A bundled fallback shipped in this skill's ``scripts/`` directory, so
       the script keeps working when the skill is installed standalone.
    3. An already-importable ``pyast_utils`` on ``sys.path`` (e.g. PYTHONPATH).
    """
    here = Path(__file__).resolve().parent
    for parent in (here, *here.parents):
        candidate = parent / "python-dependency-analyzer" / "scripts"
        if (candidate / "pyast_utils.py").exists():
            return candidate
    if (here / "pyast_utils.py").exists():
        return here
    try:
        import pyast_utils  # noqa: F401  already importable
        return None
    except ImportError:
        print(
            "error: shared module 'pyast_utils' not found; install the suite as a whole "
            "(cp -r python-*/) or add python-dependency-analyzer/scripts to PYTHONPATH.",
            file=sys.stderr,
        )
        sys.exit(2)


_pyast_utils_dir = _pyast_utils_scripts_dir()
if _pyast_utils_dir is not None:
    sys.path.insert(0, str(_pyast_utils_dir))
from pyast_utils import (  # noqa: E402
    FRAMEWORK_KEYWORDS,
    first_party_target,
    imported_roots,
    iter_python_files,
    module_name,
    module_set,
    resolve_relative_import,
)


def layer_for_module(module: str, layer_prefixes: list[tuple[str, str]]) -> str | None:
    for prefix, layer in layer_prefixes:
        if module == prefix or module.startswith(prefix + "."):
            return layer
    return None


def layer_prefixes_from_config(config: dict) -> list[tuple[str, str]]:
    prefixes: list[tuple[str, str]] = []
    for layer, roots in config.get("layers", {}).items():
        for root_prefix in roots:
            prefixes.append((root_prefix.replace("/", "."), layer))
    return sorted(prefixes, key=lambda item: (-len(item[0]), item[0]))


def _in_category(full: str, top: str, category: tuple[str, ...]) -> bool:
    if top in category:
        return True
    return any(full == key or full.startswith(key + ".") for key in category)


def matches_entry(entry: str, target_layer: str | None, full: str, top: str) -> bool:
    if target_layer == entry:
        return True
    if top == entry or full == entry or full.startswith(entry + "."):
        return True
    category = FRAMEWORK_KEYWORDS.get(entry)
    return bool(category) and _in_category(full, top, category)


def load_config(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "layers" not in data or "forbidden" not in data:
        raise ValueError("config must contain 'layers' and 'forbidden'")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce layer-rule contracts over imports.")
    parser.add_argument("--config", required=True, help="Path to the JSON layer contract.")
    parser.add_argument("--exclude", nargs="*", default=(), help="Glob-like substrings to skip.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root to scan.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    config_path = Path(args.config).resolve()
    try:
        config = load_config(config_path)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    files = iter_python_files(root)
    modules = module_set(root, files)
    layer_index = layer_prefixes_from_config(config)

    violations: list[tuple[str, str, str, str]] = []
    for path in files:
        current = module_name(root, path)
        if not current:
            continue
        from_layer = layer_for_module(current, layer_index)
        if from_layer is None:
            continue
        for raw_import in imported_roots(path):
            target = first_party_target(raw_import, current, modules)
            target_layer = layer_for_module(target, layer_index) if target else None
            full = target or raw_import
            top = full.split(".")[0]
            for rule in config["forbidden"]:
                if rule.get("from") != from_layer:
                    continue
                for entry in rule["to"]:
                    if matches_entry(entry, target_layer, full, top):
                        violations.append(
                            (str(path.relative_to(root)), from_layer, target or raw_import, entry)
                        )
                        break

    excluded = tuple(args.exclude)
    if excluded:
        violations = [v for v in violations if not any(part in v[0] for part in excluded)]

    if violations:
        print(f"layer-rule violations: {len(violations)}")
        for path, from_layer, target, entry in sorted(set(violations)):
            print(f"- {path}: {from_layer} -> {target} (rule: {entry})")
        return 1
    print("layer-rule check: clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
