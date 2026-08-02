# Concern Ownership Map

Canonical, machine-checked ownership of overlapping concerns. The orchestrator
routes by concern; where two specialists could plausibly claim the same work,
the map assigns one primary owner per concern and records the boundary that
keeps a specialist from absorbing another's responsibility.

`scripts/validate_suite.py` enforces this map:

- Every concern has exactly one owner (a duplicate owner is an error).
- Every owner is a real skill directory.
- Every skill in the suite owns at least one concern.
- Every row has a non-empty boundary note.
- Known overlap pairs must both appear as owners of distinct concerns.

The "investigate vs enforce" and "measure vs design" splits are deliberate:
they are different concerns, not shared ownership.

## Ownership Table

| Concern | Owner | Boundary |
| --- | --- | --- |
| routing | python-agent-orchestrator | Classify intent, choose the smallest skill chain, define handoffs |
| app-architecture | python-senior-architect | Module boundaries, layering, plans, ADRs, migration strategy |
| concurrency-measure | python-performance | Measure, profile, benchmark the running system and fix the confirmed bottleneck |
| concurrency-design | python-async-architect | Design the concurrency model, worker/queue topology, backpressure, messaging |
| dependency-state | python-dependency-analyzer | Investigate and report the current import graph, cycles, and dependency health |
| layer-enforcement | python-architecture-scanner | Define and enforce layer contracts and forbidden-import rules as CI gates |
| persistence-design | python-data-architect | Data models, migrations, warehouses, and pipelines |
| implementation | python-coder | Bounded code changes from a plan or clear request |
| code-review | python-reviewer | Correctness, regressions, maintainability, and test gaps |
| test-strategy | python-testing | Test strategy, fixtures, regression and contract coverage |
| security-audit | python-security | Auth, secrets, injection, SSRF, dependencies, and tenant isolation |
| production-readiness | python-production | Deployment, observability, rollback, and incidents |

## Overlap Guard

The pairs below are the known overlap risks. Each pair must stay split into
distinct concerns in the table above; a pair sharing a concern is an error.

| Overlap pair | Split concerns |
| --- | --- |
| python-performance / python-async-architect | concurrency-measure vs concurrency-design |
| python-dependency-analyzer / python-architecture-scanner | dependency-state vs layer-enforcement |
| python-senior-architect / python-data-architect | app-architecture vs persistence-design |
| python-senior-architect / python-async-architect | app-architecture vs concurrency-design |

## Process

- Add or rename a concern only when a real overlap was observed, not preemptively.
- When a specialist would absorb another's responsibility, split it into two
  concerns with a boundary note instead of sharing one concern.
- Update the orchestrator's routing table and this map together; the validator
  treats a missing row as an error.
