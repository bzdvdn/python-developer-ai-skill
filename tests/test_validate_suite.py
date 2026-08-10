"""Tests for scripts/validate_suite.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests._loader import load

ROOT = Path(__file__).resolve().parents[1]

GOOD_FRONTMATTER = """\
---
name: python-testing
version: 0.1.0
description: A description.
metadata:
  short-description: Short.
---

# Heading
"""


class TestParseFrontmatter(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("validate_suite")

    def test_real_skill_parses(self) -> None:
        fields = self.mod.parse_frontmatter(ROOT / "python-testing" / "SKILL.md")
        self.assertIsNotNone(fields)
        assert fields is not None
        self.assertEqual(fields["name"], "python-testing")
        self.assertTrue(fields["description"])
        self.assertTrue(fields["short-description"])

    def test_missing_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "SKILL.md"
            path.write_text("# No frontmatter\n", encoding="utf-8")
            self.assertIsNone(self.mod.parse_frontmatter(path))

    def test_invalid_name_flagged(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "python-wrong-name"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(GOOD_FRONTMATTER, encoding="utf-8")
            self.mod.validate_skill(skill_dir, report)
        self.assertTrue(any("name is" in e for e in report.errors))


class TestReferenceResolution(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("validate_suite")

    def test_broken_reference_reported(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "python-test"
            skill_dir.mkdir()
            text = GOOD_FRONTMATTER + "\nUse `templates/nope.md` for output.\n"
            (skill_dir / "SKILL.md").write_text(text, encoding="utf-8")
            self.mod.validate_skill(skill_dir, report)
        self.assertTrue(any("unresolved reference" in e for e in report.errors))


class TestVersionConsistency(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("validate_suite")

    def test_mismatched_versions_flagged(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("python-a", "python-b"):
                skill_dir = root / name
                skill_dir.mkdir()
                fm = GOOD_FRONTMATTER.replace("version: 0.1.0", f"version: {1 if name == 'python-a' else 2}.0.0")
                (skill_dir / "SKILL.md").write_text(fm, encoding="utf-8")
            self.mod.validate_versions(report, root)
        self.assertTrue(any("version mismatch" in e for e in report.errors))

    def test_matching_versions_clean(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("python-a", "python-b"):
                skill_dir = root / name
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(GOOD_FRONTMATTER, encoding="utf-8")
            self.mod.validate_versions(report, root)
        self.assertEqual(report.errors, [])

    def test_changelog_version_mismatch_flagged(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("python-a", "python-b"):
                (root / name).mkdir()
                (root / name / "SKILL.md").write_text(GOOD_FRONTMATTER, encoding="utf-8")
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## [0.2.0] - 2026-01-01\n\n- something\n", encoding="utf-8"
            )
            self.mod.validate_versions(report, root)
        self.assertTrue(any("CHANGELOG" in e for e in report.errors))

    def test_readme_version_mismatch_flagged(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "python-a").mkdir()
            (root / "python-a" / "SKILL.md").write_text(GOOD_FRONTMATTER, encoding="utf-8")
            (root / "README.md").write_text("Current version: 0.3.0 (see CHANGELOG).\n", encoding="utf-8")
            self.mod.validate_versions(report, root)
        self.assertTrue(any("README" in e for e in report.errors))


class TestDuplicationDetection(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("validate_suite")

    def test_heading_duplicated_from_reference_flagged(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "python-test"
            (skill_dir / "references").mkdir(parents=True)
            (skill_dir / "references" / "dup.md").write_text("# Ref\n\n## Naming\n\n- item\n", encoding="utf-8")
            text = GOOD_FRONTMATTER + "\n## Naming\n\n- inline copy\n\nUse `references/dup.md` for depth.\n"
            (skill_dir / "SKILL.md").write_text(text, encoding="utf-8")
            self.mod.validate_duplication(skill_dir, report)
        self.assertTrue(any("duplicated in SKILL.md" in w for w in report.warnings))

    def test_distinct_headings_clean(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "python-test"
            (skill_dir / "references").mkdir(parents=True)
            (skill_dir / "references" / "dup.md").write_text("# Ref\n\n## Naming\n\n- item\n", encoding="utf-8")
            text = GOOD_FRONTMATTER + "\n## My Heading\n\n- not a copy\n\nUse `references/dup.md` for depth.\n"
            (skill_dir / "SKILL.md").write_text(text, encoding="utf-8")
            self.mod.validate_duplication(skill_dir, report)
        self.assertEqual(report.warnings, [])


class TestCacheScan(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("validate_suite")

    def test_lists_each_cache_dir_once(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pkg = root / "pkg"
            (pkg / "__pycache__").mkdir(parents=True)
            (pkg / ".pytest_cache").mkdir(parents=True)
            (pkg / "__pycache__" / "x.pyc").write_text("", encoding="utf-8")
            (pkg / ".pytest_cache" / "CACHEDIR.TAG").write_text("", encoding="utf-8")
            self.mod.check_caches(report, root)
        self.assertEqual(len(report.warnings), 2)

    def test_no_caches_clean(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pkg").mkdir()
            (root / "pkg" / "app.py").write_text("x = 1\n", encoding="utf-8")
            self.mod.check_caches(report, root)
        self.assertEqual(report.warnings, [])


class TestStdlibOnlyCheck(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("validate_suite")

    def test_flags_third_party_import(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "scan.py").write_text("import requests\nx = 1\n", encoding="utf-8")
            self.mod.validate_stdlib_only(report, root)
        self.assertTrue(any("non-stdlib" in e for e in report.errors))

    def test_clean_stdlib_only(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            (root / "scripts" / "scan.py").write_text(
                "import os, sys\nfrom pathlib import Path\nfrom pyast_utils import module_name\n",
                encoding="utf-8",
            )
            self.mod.validate_stdlib_only(report, root)
        self.assertEqual(report.errors, [])


class TestPyastUtilsCopies(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("validate_suite")

    def _make(self, tmp: str) -> tuple[Path, Path]:
        root = Path(tmp)
        canonical_dir = root / "python-dependency-analyzer" / "scripts"
        canonical_dir.mkdir(parents=True)
        canonical = canonical_dir / "pyast_utils.py"
        canonical.write_text("SHARED_CONTENT\n", encoding="utf-8")
        return root, canonical

    def _consumer(self, root: Path) -> Path:
        consumer = root / "python-async-architect" / "scripts" / "scan.py"
        consumer.parent.mkdir(parents=True)
        consumer.write_text("from pyast_utils import iter_python_files\n", encoding="utf-8")
        return consumer

    def test_missing_canonical_flagged(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            self.mod.validate_pyast_utils_copies(report, Path(tmp))
        self.assertTrue(any("canonical shared module missing" in e for e in report.errors))

    def test_missing_bundled_copy_flagged(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = self._make(tmp)
            self._consumer(root)
            self.mod.validate_pyast_utils_copies(report, root)
        self.assertTrue(any("ships no bundled" in e for e in report.errors))

    def test_drifted_bundled_copy_flagged(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root, _ = self._make(tmp)
            consumer = self._consumer(root)
            (consumer.parent / "pyast_utils.py").write_text("STALE\n", encoding="utf-8")
            self.mod.validate_pyast_utils_copies(report, root)
        self.assertTrue(any("does not match canonical" in e for e in report.errors))

    def test_matching_bundled_copy_clean(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root, canonical = self._make(tmp)
            consumer = self._consumer(root)
            bundled = consumer.parent / "pyast_utils.py"
            bundled.write_text(canonical.read_text(encoding="utf-8"), encoding="utf-8")
            self.mod.validate_pyast_utils_copies(report, root)
        self.assertEqual(report.errors, [])


class TestFrameworkKeywords(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("validate_suite")

    def test_duplicate_keyword_flagged(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical_dir = root / "python-dependency-analyzer" / "scripts"
            canonical_dir.mkdir(parents=True)
            canonical = canonical_dir / "pyast_utils.py"
            canonical.write_text(
                "FRAMEWORK_KEYWORDS = {'web': ('fastapi', 'aiohttp'), "
                "'http_client': ('requests', 'aiohttp')}\n",
                encoding="utf-8",
            )
            self.mod.validate_framework_keywords(report, root)
        self.assertTrue(any("in both" in e for e in report.errors))

    def test_clean_keywords_pass(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canonical_dir = root / "python-dependency-analyzer" / "scripts"
            canonical_dir.mkdir(parents=True)
            (canonical_dir / "pyast_utils.py").write_text(
                "FRAMEWORK_KEYWORDS = {'web': ['fastapi'], 'http_client': ['requests']}\n",
                encoding="utf-8",
            )
            self.mod.validate_framework_keywords(report, root)
        self.assertEqual(report.errors, [])


class TestConcernOwnership(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("validate_suite")

    def _make(self, tmp: str, rows: list[str], skills: list[str]) -> None:
        root = Path(tmp)
        for name in skills:
            (root / name).mkdir()
            (root / name / "SKILL.md").write_text(GOOD_FRONTMATTER, encoding="utf-8")
        ref = root / "python-agent-orchestrator" / "references"
        ref.mkdir(parents=True)
        header = "# Ownership\n\n| Concern | Owner | Boundary |\n| --- | --- | --- |\n"
        (ref / "concern-ownership.md").write_text(header + "\n".join(rows) + "\n", encoding="utf-8")

    def test_duplicate_owner_flagged(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            self._make(
                tmp,
                ["| x | python-a | one |", "| x | python-b | two |"],
                ["python-a", "python-b"],
            )
            self.mod.validate_concern_ownership(report, Path(tmp))
        self.assertTrue(any("owned by both" in e for e in report.errors))

    def test_uncovered_skill_flagged(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            self._make(tmp, ["| x | python-a | one |"], ["python-a", "python-b"])
            self.mod.validate_concern_ownership(report, Path(tmp))
        self.assertTrue(any("owns no concern" in e for e in report.errors))

    def test_unknown_owner_flagged(self) -> None:
        report = self.mod.Report()
        with tempfile.TemporaryDirectory() as tmp:
            self._make(tmp, ["| x | python-nope | one |"], ["python-a"])
            self.mod.validate_concern_ownership(report, Path(tmp))
        self.assertTrue(any("unknown owner" in e for e in report.errors))

    def test_clean_map(self) -> None:
        report = self.mod.Report()
        skills = [
            "python-agent-orchestrator", "python-senior-architect",
            "python-performance", "python-async-architect",
            "python-dependency-analyzer", "python-architecture-scanner",
            "python-data-architect",
        ]
        rows = [
            "| routing | python-agent-orchestrator | route work |",
            "| app-architecture | python-senior-architect | design |",
            "| concurrency-measure | python-performance | profile |",
            "| concurrency-design | python-async-architect | design queues |",
            "| dependency-state | python-dependency-analyzer | report graph |",
            "| layer-enforcement | python-architecture-scanner | enforce rules |",
            "| persistence-design | python-data-architect | design data |",
        ]
        with tempfile.TemporaryDirectory() as tmp:
            self._make(tmp, rows, skills)
            self.mod.validate_concern_ownership(report, Path(tmp))
        self.assertEqual(report.errors, [])


if __name__ == "__main__":
    unittest.main()
