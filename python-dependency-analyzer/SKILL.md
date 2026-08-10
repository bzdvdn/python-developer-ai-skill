---
name: python-dependency-analyzer
version: 0.1.3
license: MIT
description: Use for Python import graph analysis, package boundary inspection, circular dependency detection, layer violation detection, dependency health, external dependency inventory, and architecture drift evidence.
metadata:
  short-description: Analyze Python dependencies and imports
---

# Python Dependency Analyzer

## Mission

Make Python dependencies visible. Detect cycles, forbidden imports, leaking infrastructure, package boundary erosion, and dependency sprawl.

## Activation

Use for:
- Circular imports.
- Layering violations.
- Package organization review.
- Dependency direction analysis.
- External dependency inventory.
- Architecture scanner requests.
- Import graph reports.

## Workflow

1. Inspect project metadata and package roots.
2. Identify first-party packages.
3. Build or approximate import graph.
4. Separate first-party, third-party, and standard-library imports.
5. Detect cycles and high-fan-in or high-fan-out modules.
6. Check imports against expected layers.
7. Report evidence and remediation options.

## Tools

Use available:
- `rg` for imports.
- `python -m compileall` for import-time syntax signals.
- `import-linter` for contracts.
- `grimp` for import graph queries.
- `pydeps` for visualization.
- `pipdeptree`, `uv pip tree`, or `poetry show --tree` for external dependencies.
- `deptry` for unused or missing dependencies.

## Heuristics

- Domain packages should not import web frameworks, ORM sessions, queue envelopes, cache clients, or HTTP clients directly.
- Application packages may depend on domain contracts and ports.
- Infrastructure packages may depend outward on frameworks and external libraries.
- Handlers should depend on application services, not repositories directly unless local architecture intentionally allows it.
- Shared modules with high fan-out deserve scrutiny.
- Cycles involving settings, models, and app initialization often indicate import-time side effects.
- Test imports can violate production layering intentionally, but should not hide production cycles.

## Examples

Circular import:
- Request: "Find why importing the app fails with a circular import."
- Do: locate the import chain, separate runtime imports from type-only imports, and identify the smallest boundary that breaks the cycle.
- Watch: package `__init__.py` side effects, settings imported by domain modules, and fixes that only move the cycle elsewhere.

Layer violation:
- Request: "Check whether domain imports infrastructure."
- Do: define first-party package roots, classify layers from evidence, search imports, and report concrete offending edges.
- Watch: framework objects in domain packages, ORM sessions crossing inward, and test-only imports mixed with production imports.

External dependency inventory:
- Request: "Explain dependency sprawl in this service."
- Do: inspect project metadata and lock/tree output, group dependencies by purpose, and identify unused or overlapping libraries.
- Watch: multiple HTTP clients, abandoned packages, unpinned runtime dependencies, and transitive dependencies carrying production risk.

## What To Watch

- Define package roots before drawing conclusions from imports.
- Separate first-party, third-party, standard-library, and test-only imports.
- A cycle report should include the concrete import path, not just module names.
- Layer rules should reflect the repo's intended architecture when documented.
- Remediation should prefer moving dependency direction over hiding imports locally.

## Good / Bad

Good:
- Establishes first-party package roots and expected layers from repo evidence.
- Reports concrete import edges and cycle paths.
- Separates production imports from tests and type-only imports.
- Distinguishes dependency-health issues from architecture-boundary issues.
- Suggests enforceable contracts or small remediation steps.

Bad:
- Declares layer violations before defining layers.
- Mixes stdlib, third-party, first-party, and test imports in one undifferentiated list.
- Reports "circular dependency" without the import chain.
- Fixes cycles by moving imports into functions without addressing boundary design.
- Recommends package reshuffles without considering public import compatibility.

## Output

Use `templates/dependency-analysis.md` when a structured dependency report is useful. The template covers scope, package roots, import graph summary, cycles, layer violations, high-risk modules, external dependency notes, recommendations, and suggested contracts.

For reproducible evidence, use `scripts/import_graph.py` to produce the import graph, cycles, and fan-in/fan-out baseline.

`scripts/pyast_utils.py` holds the shared, dependency-free filesystem/AST helpers used by
this skill and by the architecture scanner, architect report, and async blocking detector.
Keep shared scanning logic there instead of duplicating it; `scripts/validate_suite.py`
enforces that all suite scripts, including it, import only the standard library.

## Definition Of Done

Dependency analysis is complete when:
- First-party package roots are identified from repository evidence.
- Imports are separated into first-party, third-party, standard-library, type-only, and test-only where practical.
- Cycles include concrete import paths, not only module names.
- Layer violations reference expected layer rules and concrete offending imports.
- High-fan-in, high-fan-out, and dependency-health concerns are evidence-based.
- Remediation favors boundary repair and enforceable contracts over hiding imports locally.
