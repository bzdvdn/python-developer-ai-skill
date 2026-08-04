#!/usr/bin/env python3
"""Detect likely blocking calls inside async functions.

Dependency-free baseline for async reviews. Flags calls to known-blocking APIs
(``time.sleep``, ``requests.*``, ``subprocess.run/call/Popen``, ``os.system``,
``urllib.request.urlopen``, ``.recv()`` on sockets) that appear anywhere inside an
``async def`` body, including nested functions. Sync ``def`` helpers defined outside
async functions are not scanned, and code handed to ``asyncio.run_in_executor`` or
``asyncio.to_thread`` is not flagged (that is the safe pattern): a lambda or nested
function passed to an executor runs off the event loop, so its subtree is excluded
from the scan, including when the callable is handed over through a local variable.

The check is a heuristic, not proof. Exit code 0 = no hits, 1 = hits found.
Filesystem and AST helpers are imported from the shared ``pyast_utils`` module
in ``python-dependency-analyzer/scripts`` (see that module). The import
resolves the canonical suite copy when the suite is installed as a whole and
falls back to a bundled copy shipped in this skill so the script also works
when the skill is installed standalone.

Usage:
    python3 detect_async_blocking.py [root]
"""

from __future__ import annotations

import argparse
import ast
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
    callable_name,
    iter_python_files,
)

BLOCKING_CALLS: set[str] = {
    "time.sleep",
    "requests.get", "requests.post", "requests.put", "requests.delete",
    "requests.patch", "requests.head", "requests.options", "requests.request",
    "subprocess.run", "subprocess.call", "subprocess.Popen", "subprocess.check_call",
    "os.system", "os.popen",
    "urllib.request.urlopen",
    "socket.recv", "socket.send",
}

BLOCKING_PREFIXES: tuple[str, ...] = (
    "requests.",
    "boto3.",
    "google.cloud.storage.",
    "azure.storage.",
)

EXECUTOR_CALLS: tuple[str, ...] = (
    "asyncio.run_in_executor",
    "asyncio.to_thread",
)


def _is_executor_call(name: str) -> bool:
    """True for ``asyncio.run_in_executor``/``asyncio.to_thread`` and any
    ``<obj>.run_in_executor``/``<obj>.to_thread`` spelling (``loop.run_in_executor``,
    ``self._loop.run_in_executor``, a stored executor, ...). Matches by suffix so the
    executor-argument logic in :func:`_offloaded_nodes` and the call detection agree.
    """
    return bool(name) and (name.endswith("run_in_executor") or name.endswith("to_thread"))


def _offloaded_nodes(async_func: ast.AsyncFunctionDef) -> set[ast.AST]:
    """Return lambdas and nested functions inside ``async_func`` that are passed to
    an executor (``run_in_executor``/``to_thread``). Those run off the event loop, so
    blocking calls in their subtrees are safe and must not be flagged.

    The argument is tracked through simple local aliasing too: a lambda or nested
    function assigned to a variable and then passed to the executor is still offloaded
    (``fn = lambda: requests.get(url); await run_in_executor(None, fn)``). Both
    assignment-before-call and call-before-assignment orders are recognized.
    """
    nested_defs: dict[str, ast.FunctionDef] = {}
    for child in ast.walk(async_func):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child is not async_func:
            nested_defs.setdefault(child.name, child)

    assigned: dict[str, ast.AST] = {}
    for child in ast.walk(async_func):
        target: ast.expr | None = None
        value: ast.expr | None = None
        if isinstance(child, ast.Assign) and len(child.targets) == 1:
            target, value = child.targets[0], child.value
        elif isinstance(child, ast.AnnAssign):
            target, value = child.target, child.value
        elif isinstance(child, ast.NamedExpr):
            target, value = child.target, child.value
        if not isinstance(target, ast.Name) or value is None:
            continue
        if isinstance(value, ast.Lambda):
            assigned[target.id] = value
        elif isinstance(value, ast.Name) and value.id in nested_defs:
            assigned[target.id] = nested_defs[value.id]

    safe: set[ast.AST] = set()
    for child in ast.walk(async_func):
        if not isinstance(child, ast.Call):
            continue
        name = callable_name(child.func)
        if not _is_executor_call(name):
            continue
        func_arg: ast.AST | None = None
        if name.endswith("run_in_executor") and len(child.args) >= 2:
            func_arg = child.args[1]
        elif name.endswith("to_thread") and len(child.args) >= 1:
            func_arg = child.args[0]
        if isinstance(func_arg, ast.Lambda):
            safe.add(func_arg)
        elif isinstance(func_arg, ast.Name):
            offloaded = assigned.get(func_arg.id) or nested_defs.get(func_arg.id)
            if offloaded is not None:
                safe.add(offloaded)
    return safe


def _blocking_calls_in(nodes: set[ast.AST]) -> set[ast.AST]:
    calls: set[ast.AST] = set()
    for node in nodes:
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                calls.add(sub)
    return calls


def detect(path: Path) -> list[tuple[int, str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return []
    hits: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        safe_calls = _blocking_calls_in(_offloaded_nodes(node))
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            name = callable_name(child.func)
            if not name:
                continue
            if name in BLOCKING_CALLS or name.startswith(BLOCKING_PREFIXES):
                if child in safe_calls:
                    continue
                hits.append((child.lineno, name))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect likely blocking calls inside async functions.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root to scan.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    all_hits: list[tuple[str, int, str]] = []
    for path in iter_python_files(root):
        for lineno, name in detect(path):
            all_hits.append((str(path.relative_to(root)), lineno, name))

    if all_hits:
        print(f"possible blocking calls in async code: {len(all_hits)}")
        for path, lineno, name in all_hits:
            print(f"- {path}:{lineno}: {name}")
        return 1
    print("async blocking check: no hits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
