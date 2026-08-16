---
name: python-agent-orchestrator
version: 0.1.4
license: MIT
description: Use when a Python request spans multiple specialist skills or needs routing across architect, coder, reviewer, testing, security, performance, production, dependency analysis, scanning, data, or async architecture. Classifies the task, chooses the smallest skill chain, and defines handoff contracts.
metadata:
  short-description: Route Python work across specialist skills
---

# Python Agent Orchestrator

## Mission

Route Python development work to the smallest reliable set of specialist skills. Preserve clear ownership, handoff contracts, and validation flow.

## Skill Roles

- `python-senior-architect`: architecture, design, ADRs, implementation plans, migration strategy.
- `python-coder`: bounded implementation, refactoring execution, bug fixes, CLI/API/library code changes.
- `python-reviewer`: code and PR review for correctness, regressions, maintainability, and test gaps.
- `python-testing`: test strategy, fixtures, regression tests, contract tests, integration tests.
- `python-security`: auth, secrets, unsafe input, dependency risk, tenant isolation, secure defaults.
- `python-performance`: profiling, database performance, async bottlenecks, caching, throughput.
- `python-production`: deployment, config, observability, rollback, incidents, operational readiness.
- `python-dependency-analyzer`: import graph, cycles, layer rules, package boundaries, dependency health.
- `python-architecture-scanner`: enforce layer contracts, forbidden-import rules, CI gates, package metrics.
- `python-data-architect`: persistence, data models, migrations, warehouses, pipelines.
- `python-async-architect`: event loops, workers, queues, backpressure, concurrency, messaging.

## Routing Rules

Start with the skill that owns the dominant risk, using this intent table:

| Intent | Start skill |
| --- | --- |
| Design, boundaries, migration, architecture risk | `python-senior-architect` |
| Localized change, obvious design, bug fix | `python-coder` |
| Coverage, regression safety, failing tests | `python-testing` |
| Review / PR feedback | `python-reviewer` |
| Auth, secrets, validation, CVEs, SSRF, tenant isolation | `python-security` |
| Slowness, memory, latency, throughput, profiling, benchmarks | `python-performance` |
| Deployment, rollback, observability, incidents | `python-production` |
| Import cycles, layering, dependency sprawl | `python-dependency-analyzer` |
| Enforce layer rules, CI gates, package metrics | `python-architecture-scanner` |
| Schemas, migrations, warehouses, pipelines | `python-data-architect` |
| Event loops, worker/queue topology, backpressure, concurrency model, messaging | `python-async-architect` |

- Start with Architect when design, boundaries, migrations, or architecture risk are unclear.
- Start with Coder when the requested change is localized and the design is obvious.
- Start with Testing when the goal is coverage, regression safety, or failing test repair.
- Start with Reviewer when the user asks for review or PR feedback.
- Start with Security when the request involves auth, authorization, secrets, validation, dependency CVEs, SSRF, injection, or tenant boundaries.
- Start with Performance when the request involves measuring or improving slowness, memory, latency, throughput, database load, or profiling.
- Start with Production when the request involves deployment, rollback, monitoring, logging, alerting, runbooks, migrations, or incidents.
- Start with Dependency Analyzer when the request involves import cycles, layering, package layout, dependency sprawl, or forbidden imports.
- Start with Architecture Scanner when the request involves enforcing layer contracts, CI architecture gates, or package metrics.
- Start with Data Architect when the request involves schema design, data models, migrations, warehouses, or pipelines.
- Start with Async Architect when the request involves designing the concurrency model, worker/queue topology, backpressure, or messaging.

### Disambiguating Overlap

The canonical concern-to-owner map lives in `references/concern-ownership.md` and is
validated by `scripts/validate_suite.py`: one owner per concern, every skill covered,
and known overlap pairs forced into distinct concerns. Treat the map as the contract;
this section summarizes it.

- Performance vs Async Architect: Performance measures and improves the running system
  (profiling, benchmarks, query counts, latency). Async Architect designs the concurrency
  model, worker/queue topology, and messaging. "Blocking calls in async code" is a
  Performance measurement; "how workers and queues should be shaped" is Async Architect
  design.
- Dependency Analyzer vs Architecture Scanner: Dependency Analyzer investigates and
  reports the current state; Architecture Scanner defines and enforces contracts and CI gates.
- Senior Architect vs Data/Async Architect: Senior Architect owns application and module
  architecture; Data Architect owns persistence; Async Architect owns the async and message
  layer. Start with the specialist when the concern is exclusively theirs.

## Handoff Format

Use `templates/handoff.md` for every handoff. Fill all sections; a vague handoff forces the next skill to redesign the task.

```markdown
# Handoff
## Target Skill
## Objective
## Scope
## Out Of Scope
## Context
## Constraints
## Files Or Modules
## Expected Output
## Validation
## Risks
## Definition Of Done
```

## Sequencing Patterns

- New feature with unclear boundaries: Architect -> Coder -> Testing -> Reviewer.
- Small bug: Coder -> Testing -> Reviewer.
- Refactor: Architect -> Dependency Analyzer -> Coder -> Testing -> Reviewer.
- PR review: Reviewer -> Architect/Security/Performance only if those risks appear.
- Production incident: Production -> Performance/Security/Architect as evidence requires -> Coder -> Testing -> Reviewer.
- Security-sensitive change: Security -> Architect if boundary impact exists -> Coder -> Testing -> Reviewer.

## Examples

Localized implementation:
- Request: "Fix the CLI crash when config is missing."
- Route: Coder -> Testing -> Reviewer.
- Watch: do not involve Architect unless the fix exposes config-boundary redesign.

Cross-boundary feature:
- Request: "Add recurring billing with webhooks and background reconciliation."
- Route: Architect -> Security -> Coder -> Testing -> Production -> Reviewer.
- Watch: auth/webhook trust boundaries, idempotency, persistence contracts, migration order, and operational visibility.

Performance complaint:
- Request: "Checkout is slow under load."
- Route: Performance -> Coder if fix is local, or Architect first if the bottleneck requires boundary redesign.
- Watch: evidence before implementation, database/query ownership, and regression benchmarks.

Architecture drift:
- Request: "Find and fix layer violations."
- Route: Dependency Analyzer -> Architect -> Coder -> Testing -> Reviewer.
- Watch: import graph evidence, intended layer rules, phased remediation, and tests or contracts that prevent recurrence.

## What To Watch

- Use the smallest skill chain that covers the real risk.
- Route based on task intent and blast radius, not keyword matching alone.
- Each handoff needs scope, out-of-scope, expected output, validation, and risks.
- Do not let one skill silently absorb another skill's responsibility.
- Stop routing when the next step is obvious and locally executable.

## Stop Conditions

Stop orchestrating and execute locally when:
- The next action is a bounded implementation, test, review, or report that has a clear owner.
- The selected skill has enough scope, files, constraints, validation, and definition of done to proceed.
- Additional specialists would only restate generic best practices.
- The user explicitly asks for a direct answer or localized change.

Pause and ask for clarification only when:
- The requested outcome changes public behavior and the desired behavior is not inferable.
- Two valid routes have materially different cost, risk, or delivery timelines.
- A required credential, environment, production fact, or business rule is missing.

## Conflict Resolution

- Security, data integrity, and production rollback concerns override delivery convenience.
- Repository evidence overrides generic architecture preferences.
- Local conventions override suite defaults unless they create correctness, security, or operational risk.
- When specialists disagree, state the conflict, choose the safer reversible path, and document the trade-off.
- If a Coder implementation discovers design risk, route back to Architect before widening the change.
- If Reviewer finds a blocking correctness, security, migration, or compatibility issue, route back to the owner skill before approval.

## Good / Bad

Good:
- Classifies the request by intent, risk, and blast radius.
- Chooses the shortest specialist sequence that can handle the work safely.
- Gives each skill a bounded handoff with scope, constraints, validation, and risks.
- Revises the route when new evidence shows security, production, performance, or architecture impact.
- Stops orchestrating once execution is clear.

Bad:
- Routes every task through every skill.
- Chooses specialists by keyword only.
- Sends implementation work to Architect or review work to Coder.
- Produces vague handoffs that force the next skill to redesign the task.
- Keeps planning after the next concrete action is obvious.

## Guardrails

- Do not route to every skill by default.
- Do not let Architect implement large changes.
- Do not let Coder redesign architecture silently.
- Do not let Reviewer rewrite code unless asked.
- Do not skip validation for production, security, migration, or persistence work.
- Prefer the smallest chain that covers the risk.

## Definition Of Done

An orchestration pass is complete when:
- The task intent, risk level, and blast radius are classified.
- The selected skill sequence is the shortest credible path.
- Each handoff has objective, scope, out-of-scope, files or modules, constraints, validation, risks, and definition of done.
- Any specialist conflict is resolved or explicitly escalated.
- The next concrete action is obvious and owned by one skill.
