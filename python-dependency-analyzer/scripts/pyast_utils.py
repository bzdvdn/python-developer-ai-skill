#!/usr/bin/env python3
"""Shared, dependency-free Python source-scanning helpers for skill scripts.

Single source of truth for the filesystem and AST utilities used by several
skill scripts (import graph, layer rules, architecture report, async blocking
detection). Standard library only; ``scripts/validate_suite.py`` enforces that
every script in the suite, including this module, imports only the standard
library.

Cross-skill import: scripts that live in another skill directory add this
module's directory to ``sys.path`` relative to ``__file__``, then import it.
The suite must be installed as a whole (``cp -r python-*/``) for those imports
to resolve; see ``INSTALL.md``.
"""

from __future__ import annotations

import ast
from pathlib import Path

IGNORED_DIRS = {
    ".git", ".hg", ".mypy_cache", ".nox", ".pytest_cache", ".ruff_cache",
    ".tox", ".venv", "__pycache__", "build", "dist", "node_modules",
    "site-packages", "venv",
}

# Canonical framework keyword categories shared by the architecture report and
# the layer-rule scanner. A "to" entry in a layer contract can reference a
# category name directly (for example "web" or "orm").
#
# Invariant: a keyword belongs to at most one category. A category captures the
# dominant, unambiguous role of each keyword so the layer-rule scanner and the
# architecture report both produce one deterministic match per import. If a
# library is genuinely multi-role (for example aiohttp or redis), pick its most
# distinctive category and do not duplicate it. ``scripts/validate_suite.py``
# enforces this uniqueness; regenerate copied fallbacks with
# ``scripts/sync_pyast_utils.py``.
FRAMEWORK_KEYWORDS: dict[str, tuple[str, ...]] = {
    "web": ("fastapi", "starlette", "uvicorn", "flask", "django", "aiohttp"),
    "http_client": ("httpx", "requests", "urllib3"),
    "orm": ("sqlalchemy", "django.db", "peewee", "tortoise", "pony"),
    "validation": ("pydantic", "marshmallow"),
    "queue": ("celery", "aio_pika", "pika", "kafka", "confluent_kafka", "rq"),
    "cache": ("redis", "memcache", "aiocache"),
    "storage": ("boto3", "minio", "google.cloud.storage", "azure.storage"),
}


def iter_python_files(root: Path) -> list[Path]:
    """Return sorted ``.py`` files under ``root``, skipping generated/vendored dirs."""
    files: list[Path] = []
    for path in root.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        files.append(path)
    return sorted(files)


def module_name(root: Path, path: Path) -> str:
    """Map a file path to its dotted module name relative to ``root``."""
    rel = path.relative_to(root).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def module_set(root: Path, files: list[Path]) -> set[str]:
    """Return the set of non-empty module names for a list of files."""
    return {module_name(root, path) for path in files if module_name(root, path)}


class _RuntimeImports(ast.NodeVisitor):
    """Collect imports, skipping ``if TYPE_CHECKING:`` blocks entirely.

    ``if TYPE_CHECKING:`` imports are compile-time only: they are never
    executed at runtime and cannot participate in real import cycles, so the
    import graph (and any cycle/layer analysis built on it) must ignore them.
    """

    def __init__(self) -> None:
        self.imports: set[str] = set()

    def visit_If(self, node: ast.If) -> None:
        if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
            return
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.add(node.module)
        elif node.level:
            self.imports.add("." * node.level)
        self.generic_visit(node)


def _walk_runtime_imports(tree: ast.AST, resolve: bool) -> set[str]:
    """Run the runtime-only import walk, optionally preserving relative levels."""
    visitor = _RuntimeImports()
    visitor.visit(tree)
    if resolve:
        return {imp for imp in visitor.imports if not imp.startswith(".")}
    return visitor.imports


def parse_imports(path: Path) -> set[str]:
    """Return imported module names as written (absolute modules only).

    ``if TYPE_CHECKING:`` imports are excluded: they are never executed at
    runtime and therefore not part of the module's real dependency set.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    return _walk_runtime_imports(tree, resolve=True)


def imported_roots(path: Path) -> set[str]:
    """Return runtime imports with relative levels preserved for first-party resolution.

    ``if TYPE_CHECKING:`` imports are excluded for the same reason as in
    ``parse_imports``.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    return _walk_runtime_imports(tree, resolve=False)


def resolve_relative_import(current: str, raw_import: str) -> str | None:
    """Resolve a possibly-relative import to its absolute dotted name."""
    if not raw_import.startswith("."):
        return raw_import
    level = len(raw_import) - len(raw_import.lstrip("."))
    suffix = raw_import[level:]
    current_parts = current.split(".")
    base = current_parts[: max(0, len(current_parts) - level)]
    if suffix:
        base.extend(suffix.split("."))
    return ".".join(part for part in base if part) or None


def first_party_target(raw_import: str, current: str, modules: set[str]) -> str | None:
    """Return the longest first-party module prefix the import resolves to."""
    resolved = resolve_relative_import(current, raw_import)
    if not resolved:
        return None
    parts = resolved.split(".")
    for idx in range(len(parts), 0, -1):
        candidate = ".".join(parts[:idx])
        if candidate in modules:
            return candidate
    return None


def callable_name(node: ast.AST) -> str | None:
    """Return the dotted name of a callable AST node, or None if not resolvable."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = callable_name(node.value)
        if base:
            return f"{base}.{node.attr}"
    return None


def resolve_top_level(module: str) -> str:
    """Return the top-level package name of a dotted module name."""
    return module.split(".")[0]
