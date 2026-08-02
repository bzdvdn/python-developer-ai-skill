"""Tests for scripts/sync_pyast_utils.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests._loader import load


class TestSyncPyastUtils(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("sync_pyast_utils")

    def _make(self) -> tuple[Path, Path]:
        root = Path(tempfile.mkdtemp())
        canonical_dir = root / "python-dependency-analyzer" / "scripts"
        canonical_dir.mkdir(parents=True)
        canonical = canonical_dir / "pyast_utils.py"
        canonical.write_text("SHARED_CONTENT\n", encoding="utf-8")
        return root, canonical

    def _consumer(self, root: Path) -> tuple[Path, Path]:
        consumer = root / "python-async-architect" / "scripts" / "scan.py"
        consumer.parent.mkdir(parents=True)
        consumer.write_text("from pyast_utils import iter_python_files\n", encoding="utf-8")
        return consumer, consumer.parent / "pyast_utils.py"

    def test_ignores_canonical_skill(self) -> None:
        root, _ = self._make()
        (root / "python-dependency-analyzer" / "scripts" / "import_graph.py").write_text(
            "from pyast_utils import module_name\n", encoding="utf-8"
        )
        self.assertEqual(self.mod.sync(root, check=True), [])

    def test_check_reports_drift(self) -> None:
        root, _ = self._make()
        _, bundled = self._consumer(root)
        bundled.write_text("STALE\n", encoding="utf-8")
        problems = self.mod.sync(root, check=True)
        self.assertTrue(any("does not match canonical" in p for p in problems))

    def test_sync_writes_and_heals(self) -> None:
        root, canonical = self._make()
        _, bundled = self._consumer(root)
        self.mod.sync(root, check=False)
        self.assertEqual(bundled.read_text(encoding="utf-8"), canonical.read_text(encoding="utf-8"))
        self.assertEqual(self.mod.sync(root, check=True), [])

    def test_missing_canonical(self) -> None:
        root = Path(tempfile.mkdtemp())
        self.assertEqual(self.mod.sync(root, check=True), ["canonical-missing"])


if __name__ == "__main__":
    unittest.main()