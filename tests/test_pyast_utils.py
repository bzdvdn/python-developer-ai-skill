"""Tests for python-dependency-analyzer/scripts/pyast_utils.py shared helpers."""

from __future__ import annotations

import unittest

from tests._loader import load


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