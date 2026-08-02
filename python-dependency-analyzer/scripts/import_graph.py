#!/usr/bin/env python3
"""Build a small first-party import graph for a Python repository.

This helper is intentionally dependency-free. It is not a replacement for
import-linter or grimp, but it gives a reproducible baseline for skill reports.
Filesystem and AST helpers are imported from the shared ``pyast_utils`` module
in this directory (see ``pyast_utils.py``).
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pyast_utils import (  # noqa: E402
    first_party_target,
    imported_roots,
    iter_python_files,
    module_name,
    module_set,
    resolve_relative_import,
)


def build_graph(root: Path) -> dict[str, set[str]]:
    files = iter_python_files(root)
    modules = module_set(root, files)
    graph: dict[str, set[str]] = {}

    for path in files:
        current = module_name(root, path)
        if not current:
            continue
        edges = set()
        for raw_import in imported_roots(path):
            target = first_party_target(raw_import, current, modules)
            if target and target != current:
                edges.add(target)
        graph[current] = edges

    return graph


def find_cycles(graph: dict[str, set[str]], limit: int) -> list[list[str]]:
    """Find cycles with an iterative DFS so deep import chains cannot exhaust the
    Python recursion limit.

    Mirrors the classic gray/black coloring: nodes on the current DFS path are
    ``visiting``, finished nodes are ``visited``, and a target that is still
    ``visiting`` closes a cycle from its position on the path.
    """
    cycles: list[list[str]] = []
    stack: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()
    iters: list[Iterator[str]] = []

    for node in sorted(graph):
        if len(cycles) >= limit:
            break
        if node in visited or node in visiting:
            continue

        stack.append(node)
        visiting.add(node)
        iters.append(iter(sorted(graph.get(node, ()))))
        while stack:
            if len(cycles) >= limit:
                break
            current = stack[-1]
            try:
                target = next(iters[-1])
            except StopIteration:
                stack.pop()
                iters.pop()
                visiting.discard(current)
                visited.add(current)
                continue
            if target in visiting:
                cycles.append(stack[stack.index(target):] + [target])
            elif target not in visited:
                stack.append(target)
                visiting.add(target)
                iters.append(iter(sorted(graph.get(target, ()))))
    return cycles


def fan_metrics(graph: dict[str, set[str]]) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    fan_out = sorted(((node, len(edges)) for node, edges in graph.items()), key=lambda item: (-item[1], item[0]))
    inbound: dict[str, int] = defaultdict(int)
    for edges in graph.values():
        for target in edges:
            inbound[target] += 1
    fan_in = sorted(inbound.items(), key=lambda item: (-item[1], item[0]))
    return fan_in, fan_out


def print_report(graph: dict[str, set[str]], cycles: list[list[str]], top: int) -> None:
    edge_count = sum(len(edges) for edges in graph.values())
    print("# Import Graph Summary")
    print(f"modules: {len(graph)}")
    print(f"first_party_edges: {edge_count}")
    print()

    print("## Cycles")
    if cycles:
        for cycle in cycles:
            print("- " + " -> ".join(cycle))
    else:
        print("- none detected")
    print()

    fan_in, fan_out = fan_metrics(graph)
    print("## Top Fan-In")
    for node, count in fan_in[:top]:
        print(f"- {node}: {count}")
    if not fan_in:
        print("- none")
    print()

    print("## Top Fan-Out")
    for node, count in fan_out[:top]:
        print(f"- {node}: {count}")
    if not fan_out:
        print("- none")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a simple first-party Python import graph.")
    parser.add_argument("root", nargs="?", default=".", help="Repository or package root to scan.")
    parser.add_argument("--top", type=int, default=10, help="Number of fan-in/fan-out modules to print.")
    parser.add_argument("--cycle-limit", type=int, default=20, help="Maximum cycles to print.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    graph = build_graph(root)
    cycles = find_cycles(graph, args.cycle_limit)
    print_report(graph, cycles, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
