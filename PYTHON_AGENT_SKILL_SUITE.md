# Python Developer Agent Skill Suite

This suite splits senior Python development into composable agent roles. The goal is reliable delegation: one skill should not try to be architect, implementer, reviewer, tester, security auditor, performance engineer, and production engineer at the same time.

## Skill Map

- `python-agent-orchestrator`: routes work across the suite and preserves handoff contracts.
- `python-senior-architect`: analyzes architecture, designs boundaries, creates plans, ADRs, and migration strategy.
- `python-coder`: implements bounded Python changes from a plan or clear user request.
- `python-reviewer`: reviews code and PRs for correctness, maintainability, regressions, and missing tests.
- `python-testing`: designs and implements test strategy, fixtures, and regression coverage.
- `python-security`: reviews Python systems for security risks, unsafe dependencies, auth flaws, secrets, and tenant isolation.
- `python-performance`: profiles and improves Python runtime, database, async, caching, and throughput behavior.
- `python-production`: prepares Python systems for deployment, observability, operations, incidents, and rollback.
- `python-dependency-analyzer`: inspects import graphs, package boundaries, dependency health, and layer violations.
- `python-architecture-scanner`: defines and enforces layer contracts, forbidden-import rules, and CI-gateable architecture checks.
- `python-data-architect`: designs persistence, data models, migrations, warehouses, and pipelines.
- `python-async-architect`: designs async architecture, workers, queues, backpressure, and messaging.

## Recommended Flow

1. Use `python-agent-orchestrator` when the user request spans multiple roles or the right skill is unclear.
2. Use `python-senior-architect` before implementation when boundaries, architecture, migration, or risks are unclear.
3. Use `python-coder` to implement a bounded plan.
4. Use `python-testing` when coverage, fixtures, contracts, or regression safety are central.
5. Use `python-security`, `python-performance`, or `python-production` when specialist risks matter.
6. Use `python-reviewer` before final handoff or PR approval.
7. Use `python-dependency-analyzer` when imports, package layout, or layer rules are central evidence.
8. Use `python-architecture-scanner` when a rule must be enforced deterministically or gated in CI.
9. Use `python-data-architect` when schemas, migrations, warehouses, or pipelines dominate the work.
10. Use `python-async-architect` when event loops, workers, queues, or concurrency dominate the work.

## Example Routing

- "Add billing safely" -> Architect plans boundaries -> Coder implements -> Testing covers flows -> Reviewer checks PR.
- "Find circular imports" -> Dependency Analyzer scans -> Architect interprets impact -> Coder fixes only if plan is clear.
- "This endpoint is slow" -> Performance profiles -> Architect decides design change if boundary-level -> Coder implements.
- "Prepare for production" -> Production reviews deploy, config, observability, rollback -> Testing validates critical flows.
- "Review this PR" -> Reviewer leads -> Architect joins if design or dependency direction changed.
- "Design the billing schema" -> Data Architect designs model and migration -> Architect integrates -> Coder implements -> Testing validates.
- "The queue backlog is growing" -> Async Architect reviews worker/backpressure -> Performance measures -> Coder fixes -> Production checks rollback.
- "Gate CI on layer rules" -> Architecture Scanner defines contracts -> Coder repairs violations -> Reviewer approves the gate.

## Code Quality Philosophy

- Prefer small, typed, cohesive modules.
- Prefer explicit dependencies over globals.
- Keep framework code at boundaries.
- Make side effects visible.
- Test behavior at the right layer.
- Use boring, familiar Python unless the domain justifies more.
- Fit the repository before introducing a new pattern.
- Do not let one skill silently take over another skill's job.
