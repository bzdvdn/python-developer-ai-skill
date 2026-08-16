"""Tests for python-dependency-analyzer/scripts/pyast_utils.py shared helpers."""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

from tests._loader import load

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TestRelativeImportCollection(unittest.TestCase):
    """level-relative imports must keep their dots (imported_roots).

    Regression: ``from ..x import y`` dropped the leading dots, so it was
    indistinguishable from an absolute import of a nonexistent module.
    """

    def setUp(self) -> None:
        self.mod = load("pyast_utils")

    def test_dotted_level_preserved(self) -> None:
        tree = ast.parse("from .base import b\nfrom ..svc.pricing import p\n")
        roots = self.mod._walk_runtime_imports(tree, resolve=False)
        self.assertIn(".base", roots)
        self.assertIn("..svc.pricing", roots)

    def test_absolute_imports_unchanged(self) -> None:
        tree = ast.parse("import os\nfrom collections.abc import Iterator\n")
        roots = self.mod._walk_runtime_imports(tree, resolve=False)
        self.assertIn("os", roots)
        self.assertIn("collections.abc", roots)

    def test_first_party_target_resolves_level_two(self) -> None:
        target = self.mod.first_party_target(
            "..svc.pricing", "app.domain.order", {"app", "app.svc", "app.svc.pricing"}
        )
        self.assertEqual(target, "app.svc.pricing")

    def test_imported_roots_from_file(self) -> None:
        fixture = FIXTURES / "relative_imports/app/domain/order.py"
        roots = self.mod.imported_roots(fixture)
        self.assertIn(".base", roots)
        self.assertIn("..service.pricing", roots)

    def test_resolve_true_filters_relative(self) -> None:
        tree = ast.parse("from .base import b\nimport os\n")
        absolute = self.mod._walk_runtime_imports(tree, resolve=True)
        self.assertEqual(absolute, {"os"})


class TestFrameworkCategory(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("pyast_utils")

    def test_top_level_keywords(self) -> None:
        self.assertEqual(self.mod.framework_category("fastapi"), "web")
        self.assertEqual(self.mod.framework_category("httpx"), "http_client")
        self.assertEqual(self.mod.framework_category("sqlalchemy"), "orm")
        self.assertEqual(self.mod.framework_category("pydantic"), "validation")
        self.assertEqual(self.mod.framework_category("pika"), "queue")
        self.assertEqual(self.mod.framework_category("redis"), "cache")
        self.assertEqual(self.mod.framework_category("boto3"), "storage")

    def test_dotted_keyword_shadows_top_level(self) -> None:
        # django.db is 'orm' (most specific); plain django stays 'web'.
        self.assertEqual(self.mod.framework_category("django.db"), "orm")
        self.assertEqual(self.mod.framework_category("django.db.models"), "orm")
        self.assertEqual(self.mod.framework_category("django.contrib.admin"), "web")

    def test_dotted_submodule_matches_prefix(self) -> None:
        self.assertEqual(self.mod.framework_category("google.cloud.storage.blob"), "storage")
        self.assertEqual(self.mod.framework_category("sqlalchemy.ext.asyncio"), "orm")

    def test_unknown_import_is_none(self) -> None:
        self.assertIsNone(self.mod.framework_category("yaml"))
        self.assertIsNone(self.mod.framework_category("os.path"))

    def test_catalog_keywords_map_to_their_own_category(self) -> None:
        for category, group in self.mod.FRAMEWORK_KEYWORDS.items():
            for keyword in group:
                self.assertEqual(
                    self.mod.framework_category(keyword),
                    category,
                    f"{keyword} should map to its own category {category}",
                )


if __name__ == "__main__":
    unittest.main()