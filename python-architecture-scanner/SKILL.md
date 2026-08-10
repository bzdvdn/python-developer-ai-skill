---
name: python-architecture-scanner
version: 0.1.1
license: MIT
description: Use when architecture rules must be verified deterministically, configured as machine-checkable contracts, or gated in CI. Runs layer-rule and forbidden-import scanners and package metrics, complementing python-dependency-analyzer and python-senior-architect.
metadata:
  short-description: Deterministic architecture rule checking and enforcement
---

# Python Architecture Scanner

## Mission

Make architecture rules checkable, not just debatable. Turn layer rules and dependency direction into deterministic contracts that run in CI and produce machine-readable evidence.

## Boundary vs Dependency Analyzer

- `python-dependency-analyzer` investigates and reports on the current state: where are the cycles, what does the import graph look like, why does dependency sprawl.
- This skill defines and enforces: layer contracts, forbidden-import rules, CI gates, repeatable package metrics. When a finding must become a guardrail, this skill owns it.

## Activation

Use for:
- Configuring layer contracts and forbidden-import rules.
- Running deterministic scans: import graph, architecture report, layer-rule checks.
- Gating PRs or CI on architecture rules.
- Producing package metrics and architecture-drift reports.
- Enforcing rules like "domain must not import infrastructure".

Do not use for:
- Investigative reporting of existing dependency problems (use `python-dependency-analyzer`).
- Design decisions, ADRs, or migration plans (use `python-senior-architect`).

## Workflow

1. Identify the architecture rule to enforce (from docs, architect plans, or repo conventions).
2. Map first-party package roots to layers.
3. Configure a layer contract as a checkable file.
4. Run the scanner tooling.
5. Report violations with concrete import edges.
6. Wire the check into CI or a PR gate when useful.
7. Report metrics and drift.

## Tools

- `scripts/check_layer_rules.py` — CI-gateable layer-rule enforcement (this skill).
- `python-dependency-analyzer/scripts/import_graph.py` — cycles and fan-in/fan-out baseline.
- `python-senior-architect/scripts/architecture_report.py` — package inventory, entry points, framework surface, layer-violation heuristics.
- `import-linter`, `grimp`, `pydeps` when available.

## Examples

Enforce domain isolation:
- Request: "Gate CI so domain never imports infrastructure."
- Do: define layers from package roots, add a forbidden rule from `domain` to infrastructure/third-party keywords, run `check_layer_rules.py`, wire it into CI.
- Watch: package roots that straddle layers, tests that intentionally cross boundaries, and rules that codify outdated conventions.

Drift check:
- Request: "Produce a package-metrics and drift report for the repo."
- Do: run the import-graph and architecture-report scripts, summarize metrics, compare against the documented layer contract, and report drift edges.
- Watch: metrics that are noise without an intended target.

## What To Watch

- Rules must reflect the repo's intended architecture, not generic dogma.
- A rule without a remediation path creates noise; pair detection with boundary repair.
- Tests and type-only imports may intentionally cross layers; separate them from production violations.
- Contract files are config; changing them changes the gate. Keep them reviewed like code.

## Good / Bad

Good:
- Defines layers and rules from repository evidence.
- Produces concrete import edges for every violation.
- Keeps the check deterministic and CI-gateable.
- Separates production violations from test-only and type-only imports.

Bad:
- Codifies a rule the repo does not intend to follow.
- Reports violations without the concrete import chain.
- Hides a real cycle by relaxing the contract instead of fixing the boundary.

## Output

Use `templates/architecture-contract.md` to define a layer contract and `templates/scanner-report.md` for scan output.

## Definition Of Done

Scanner work is complete when:
- Layers and rules are defined from repository evidence.
- The check is deterministic and reproducible.
- Violations are reported with concrete import edges.
- Production, test, and type-only imports are separated where practical.
- The check is wired into CI or a PR gate when the repo supports it.
- Contract changes are surfaced for review like code changes.
