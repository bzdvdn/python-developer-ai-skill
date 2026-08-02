"""Loader helpers for importing dependency-free scripts into tests."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPTS = {
    "import_graph": ROOT / "python-dependency-analyzer/scripts/import_graph.py",
    "architecture_report": ROOT / "python-senior-architect/scripts/architecture_report.py",
    "check_layer_rules": ROOT / "python-architecture-scanner/scripts/check_layer_rules.py",
    "detect_async_blocking": ROOT / "python-async-architect/scripts/detect_async_blocking.py",
    "validate_suite": ROOT / "scripts/validate_suite.py",
    "judge_eval": ROOT / "scripts/judge_eval.py",
    "sync_pyast_utils": ROOT / "scripts/sync_pyast_utils.py",
}


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS[name])
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
