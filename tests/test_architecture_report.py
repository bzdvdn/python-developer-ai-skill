"""Tests for python-senior-architect/scripts/architecture_report.py."""

from __future__ import annotations

import io
import tempfile
import unittest
import contextlib
from pathlib import Path

from tests._loader import load

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TestEntryPoints(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("architecture_report")

    def test_async_blocking_fixture_has_no_entry_points(self) -> None:
        labels = self.mod.entry_point_labels(FIXTURES / "async_blocking" / "app.py")
        self.assertEqual(labels, set())

    def test_fastapi_and_cli_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            api = temp / "api.py"
            cli = temp / "cli.py"
            api.write_text(
                "from fastapi import FastAPI\napp = FastAPI()\n"
                "@app.get('/')\ndef root(): ...\n",
                encoding="utf-8",
            )
            cli.write_text(
                "import typer\napp = typer.Typer()\n"
                "if __name__ == '__main__':\n    typer.run(app)\n",
                encoding="utf-8",
            )
            self.assertIn("ASGI/WSGI app", self.mod.entry_point_labels(api))
            self.assertIn("CLI", self.mod.entry_point_labels(cli))


class TestDomainViolations(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("architecture_report")

    def _domain_section(self, root: Path, domain_names: list[str] | None) -> str:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.mod.report(root, domain_names=domain_names)
        output = buffer.getvalue()
        start = output.index("## Domain Importing Infrastructure")
        return output[start:]

    def test_layered_fixture_reports_domain_infra(self) -> None:
        root = FIXTURES / "layered"
        section = self._domain_section(root, ["app.domain"])
        self.assertIn("Domain Importing Infrastructure", section)
        self.assertIn("app.domain.order: imports sqlalchemy", section)
        self.assertIn("app.domain.order: imports httpx", section)

    def test_unknown_domain_name_reports_none(self) -> None:
        root = FIXTURES / "layered"
        section = self._domain_section(root, ["domain"])
        # 'domain' is not a package here; the section exists but flags nothing.
        self.assertIn("Domain Importing Infrastructure", section)
        self.assertIn("- none detected", section)

    def test_entry_points_section_present(self) -> None:
        root = FIXTURES / "layered"
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.mod.report(root, domain_names=["app.domain"])
        self.assertIn("Entry Point Candidates", buffer.getvalue())


class TestFrameworkSurfaceCategorization(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("architecture_report")
        self.surface = self._surface  # alias for readability

    def _surface(self, root: Path) -> str:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.mod.report(root, domain_names=None)
        output = buffer.getvalue()
        start = output.index("## Framework Surface")
        end = output.index("## Domain Importing Infrastructure")
        return output[start:end]

    def test_django_db_categorized_as_orm_only(self) -> None:
        # django.db must resolve to 'orm' by the most-specific-keyword rule and
        # never also to 'web', matching the layer-rule scanner.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app" / "domain").mkdir(parents=True)
            (root / "app" / "domain" / "model.py").write_text(
                "from django.db import models\n", encoding="utf-8"
            )
            surface = self._surface(root)
        self.assertIn("- orm: django", surface)
        self.assertNotIn("- web:", surface)

    def test_plain_django_is_web(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app").mkdir()
            (root / "app" / "main.py").write_text("import django\n", encoding="utf-8")
            surface = self._surface(root)
        self.assertIn("- web: django", surface)
        self.assertNotIn("- orm: django", surface)


if __name__ == "__main__":
    unittest.main()
