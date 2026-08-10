#!/usr/bin/env python3
"""Produce a reproducible architecture evidence report for a Python repository.

Dependency-free baseline for architect reports. Complements
``python-dependency-analyzer/scripts/import_graph.py`` (import graph, cycles,
fan-in/fan-out). This script focuses on: package inventory, entry-point
candidates, framework surface, and layer-violation heuristics for domain
packages importing infrastructure keywords.

The layer rule is intentionally conservative: a package is treated as a
domain candidate only when it does not already contain obvious
infrastructure entry points and it matches --domain-names. Offending edges
are evidence, not final verdicts.

Filesystem and AST helpers are imported from the shared ``pyast_utils``
module in ``python-dependency-analyzer/scripts`` (see that module). The import
resolves the canonical suite copy when the suite is installed as a whole and
falls back to a bundled copy shipped in this skill so the script also works
when the skill is installed standalone.
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections import defaultdict
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
    callable_name,
    framework_category,
    iter_python_files,
    module_name,
    parse_imports,
    resolve_top_level,
)

CALL_ENTRY_POINTS: dict[str, str] = {
    "FastAPI": "ASGI/WSGI app",
    "Flask": "ASGI/WSGI app",
    "aiohttp.web": "ASGI/WSGI app",
    "uvicorn.run": "ASGI/WSGI app",
    "Typer": "CLI",
    "typer.run": "CLI",
    "argparse.ArgumentParser": "CLI",
    "Celery": "Worker/scheduler",
    "pika.BlockingConnection": "Message consumer",
    "KafkaConsumer": "Message consumer",
}

DECORATOR_ENTRY_POINTS: dict[str, str] = {
    "app.task": "Worker/scheduler",
    "celery.task": "Worker/scheduler",
    "shared_task": "Worker/scheduler",
    "click.command": "CLI",
}

INFRA_KEYWORDS: frozenset[str] = frozenset(
    keyword.split(".")[0]
    for category in FRAMEWORK_KEYWORDS.values()
    for keyword in category
)


def package_name(root: Path, path: Path) -> str:
    rel = path.relative_to(root)
    parts = list(rel.parts[:-1])
    if parts and parts[0] == "tests":
        return "tests"
    return parts[0] if parts else "<root>"


def _module_in_domains(module: str, domain_set: set[str]) -> bool:
    """True when ``module`` or any dotted ancestor is in ``domain_set``.

    With no domain names given every module is a domain candidate, matching the
    CLI help ("all non-test packages"). With names given, both a top-level package
    (``domain``) and a nested one (``app.domain``) match their own subtree.
    """
    if not domain_set:
        return True
    parts = module.split(".")
    return any(".".join(parts[: i + 1]) in domain_set for i in range(len(parts)))


def entry_point_labels(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    labels: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = callable_name(node.func)
            if name and name in CALL_ENTRY_POINTS:
                labels.add(CALL_ENTRY_POINTS[name])
            elif name and name.startswith("aio_pika"):
                labels.add("Message consumer")

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                name = callable_name(decorator)
                if name in DECORATOR_ENTRY_POINTS:
                    labels.add(DECORATOR_ENTRY_POINTS[name])
    return labels


def report(root: Path, domain_names: list[str] | None) -> None:
    files = iter_python_files(root)
    domain_set = set(domain_names or [])

    package_files: dict[str, list[Path]] = defaultdict(list)
    entry_points: list[tuple[str, str]] = []
    framework_usage: dict[str, set[str]] = defaultdict(set)
    domain_infra: list[tuple[str, str, str]] = []

    for path in files:
        pkg = package_name(root, path)
        module = module_name(root, path)
        package_files[pkg].append(path)
        text = path.read_text(encoding="utf-8", errors="ignore")

        for label in entry_point_labels(path):
            entry_points.append((label, str(path.relative_to(root))))

        imports = parse_imports(path)
        # Categorize each import by its single canonical framework keyword category
        # (see pyast_utils.framework_category): a dotted keyword such as
        # django.db resolves to 'orm', never simultaneously to 'web'.
        for raw in imports:
            category = framework_category(raw)
            if category is not None:
                framework_usage[category].add(resolve_top_level(raw))

        is_domain = _module_in_domains(module, domain_set) and pkg != "tests"
        if is_domain:
            for raw in imports:
                top = resolve_top_level(raw)
                if top in INFRA_KEYWORDS:
                    domain_infra.append((module, str(path.relative_to(root)), top))

    print("# Architecture Evidence Report")
    print(f"root: {root}")
    print(f"python_files: {len(files)}")
    print()

    print("## Package Inventory")
    for pkg in sorted(package_files):
        print(f"- {pkg}: {len(package_files[pkg])} files")
    print()

    print("## Entry Point Candidates")
    if entry_points:
        for label, path in sorted(entry_points):
            print(f"- {label}: {path}")
    else:
        print("- none detected")
    print()

    print("## Framework Surface")
    if framework_usage:
        for category in sorted(framework_usage):
            tops = sorted(framework_usage[category])
            print(f"- {category}: {', '.join(tops)}")
    else:
        print("- none detected")
    print()

    print("## Domain Importing Infrastructure (heuristic)")
    if domain_infra:
        seen: set[tuple[str, str]] = set()
        for module, path, top in sorted(domain_infra):
            if (module, top) in seen:
                continue
            seen.add((module, top))
            print(f"- {module}: imports {top} ({path})")
        if not domain_set:
            print()
            print("note: no --domain-names given; all non-test packages treated as domain candidates.")
    else:
        print("- none detected")


def main() -> int:
    parser = argparse.ArgumentParser(description="Produce a reproducible architecture evidence report.")
    parser.add_argument("root", nargs="?", default=".", help="Repository or package root to scan.")
    parser.add_argument(
        "--domain-names",
        nargs="*",
        default=None,
        help="Package names treated as domain candidates. Default: all non-test packages.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        parser.error(f"path does not exist: {root}")
    report(root, args.domain_names)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
