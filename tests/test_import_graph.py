"""Tests for python-dependency-analyzer/scripts/import_graph.py."""

from __future__ import annotations

import unittest
from pathlib import Path

from tests._loader import load

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class TestModuleName(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("import_graph")

    def test_regular_module(self) -> None:
        root = FIXTURES / "cyclic"
        path = root / "app" / "a.py"
        self.assertEqual(self.mod.module_name(root, path), "app.a")

    def test_init_module(self) -> None:
        root = FIXTURES / "cyclic"
        path = root / "app" / "__init__.py"
        self.assertEqual(self.mod.module_name(root, path), "app")


class TestResolveRelative(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("import_graph")

    def test_absolute(self) -> None:
        self.assertEqual(self.mod.resolve_relative_import("app.a", "app.b"), "app.b")

    def test_relative_one_level(self) -> None:
        self.assertEqual(self.mod.resolve_relative_import("app.a", ".b"), "app.b")

    def test_relative_two_levels(self) -> None:
        self.assertEqual(self.mod.resolve_relative_import("app.domain.order", "..application.x"), "app.application.x")


class TestBuildGraphAndCycles(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("import_graph")

    def test_cycles_detected(self) -> None:
        root = FIXTURES / "cyclic"
        graph = self.mod.build_graph(root)
        cycles = self.mod.find_cycles(graph, limit=10)
        self.assertTrue(cycles, "expected at least one cycle")
        first = cycles[0]
        self.assertEqual(first[0], first[-1], "cycle should close back to its start")

    def test_fan_out(self) -> None:
        root = FIXTURES / "cyclic"
        graph = self.mod.build_graph(root)
        _fan_in, fan_out = self.mod.fan_metrics(graph)
        by_name = dict(fan_out)
        self.assertEqual(by_name["app.a"], 1)
        self.assertEqual(by_name["app.c"], 0)

    def test_deep_graph_no_recursion_error(self) -> None:
        # A chain longer than the default recursion limit must not crash the
        # iterative cycle search; the closing edge is still detected.
        graph: dict[str, set[str]] = {}
        depth = 2000
        for i in range(depth):
            graph[f"m{i}"] = {f"m{i + 1}"}
        graph[f"m{depth}"] = {"m0"}
        cycles = self.mod.find_cycles(graph, limit=5)
        self.assertTrue(cycles, "expected the closing cycle")
        self.assertEqual(cycles[0][0], cycles[0][-1], "cycle should close back to its start")
        self.assertEqual(cycles[0][0], "m0")

    def test_disjoint_components(self) -> None:
        graph = {
            "a": {"b"},
            "b": {"a"},
            "c": {"d"},
            "d": {"c"},
        }
        cycles = self.mod.find_cycles(graph, limit=10)
        self.assertEqual(len(cycles), 2)
        for cycle in cycles:
            self.assertEqual(cycle[0], cycle[-1])


if __name__ == "__main__":
    unittest.main()
