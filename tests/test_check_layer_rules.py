"""Tests for python-architecture-scanner/scripts/check_layer_rules.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests._loader import load

FIXTURES = Path(__file__).resolve().parent / "fixtures"

CONTRACT = {
    "layers": {
        "domain": ["app/domain"],
        "application": ["app/application"],
        "handlers": ["app/handlers"],
    },
    "forbidden": [
        {"from": "domain", "to": ["handlers", "web", "orm", "http_client"]},
        {"from": "application", "to": ["handlers"]},
    ],
}


class TestLayerMatching(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("check_layer_rules")

    def test_prefix_normalization(self) -> None:
        prefixes = self.mod.layer_prefixes_from_config(CONTRACT)
        dotted = [prefix for prefix, _layer in prefixes]
        self.assertIn("app.domain", dotted)
        self.assertNotIn("app/domain", dotted)

    def test_matches_layer_name(self) -> None:
        self.assertTrue(self.mod.matches_entry("handlers", "handlers", "app", "app"))

    def test_matches_top_level_module(self) -> None:
        self.assertTrue(self.mod.matches_entry("requests", None, "requests", "requests"))

    def test_matches_keyword_category(self) -> None:
        self.assertTrue(self.mod.matches_entry("orm", None, "sqlalchemy", "sqlalchemy"))
        self.assertTrue(self.mod.matches_entry("http_client", None, "httpx", "httpx"))

    def test_matches_dotted_keyword_by_full_import(self) -> None:
        self.assertTrue(self.mod.matches_entry("orm", None, "django.db.models", "django"))
        self.assertTrue(self.mod.matches_entry("storage", None, "google.cloud.storage.blob", "google"))

    def test_does_not_match_unrelated(self) -> None:
        self.assertFalse(self.mod.matches_entry("orm", None, "httpx", "httpx"))
        self.assertFalse(self.mod.matches_entry("web", None, "sqlalchemy", "sqlalchemy"))
        self.assertFalse(self.mod.matches_entry("cache", None, "kafka", "kafka"))


class TestCheckLayerRules(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("check_layer_rules")

    def _run(self, root: Path, extra: list[str] | None = None) -> tuple[int, str]:
        import contextlib
        import io
        import sys

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(CONTRACT, fh)
            contract_path = fh.name
        try:
            argv = ["check_layer_rules", "--config", contract_path, str(root), *(extra or [])]
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                with contextlib.redirect_stderr(buffer):
                    code = self._call_main(argv)
            return code, buffer.getvalue()
        finally:
            Path(contract_path).unlink()

    def _call_main(self, argv: list[str]) -> int:
        import sys

        old = sys.argv
        sys.argv = argv
        try:
            return self.mod.main()
        finally:
            sys.argv = old

    def test_layered_fixture_reports_violations(self) -> None:
        code, output = self._run(FIXTURES / "layered")
        self.assertEqual(code, 1, output)
        self.assertIn("domain", output)
        self.assertIn("sqlalchemy", output)

    def test_exclude_suppresses_violations(self) -> None:
        code, output = self._run(FIXTURES / "layered", extra=["--exclude", "checkout.py"])
        # domain/order.py still violates; checkout.py excluded.
        self.assertEqual(code, 1, output)
        self.assertNotIn("checkout.py", output)
        self.assertIn("sqlalchemy", output)

    def test_clean_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, output = self._run(Path(tmp))
            self.assertEqual(code, 0, output)

    def test_output_names_the_matched_rule(self) -> None:
        code, output = self._run(FIXTURES / "layered")
        self.assertEqual(code, 1, output)
        self.assertIn("(rule: orm)", output)
        self.assertIn("(rule: http_client)", output)


if __name__ == "__main__":
    unittest.main()
