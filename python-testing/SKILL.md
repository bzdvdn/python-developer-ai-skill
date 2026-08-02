---
name: python-testing
version: 0.1.0
license: MIT
description: Use for Python test strategy, regression coverage, pytest design, fixtures, factories, async tests, integration tests, contract tests, and validation planning. This skill designs or implements tests according to existing project conventions.
metadata:
  short-description: Design and implement Python tests
---

# Python Testing

## Mission

Build the right safety net for Python changes. Prefer behavior-focused tests at the cheapest reliable layer.

## Activation

Use for:
- Adding or repairing tests.
- Designing test strategy.
- Covering regressions.
- Improving fixtures or factories.
- Async, persistence, adapter, contract, or integration testing.

Do not use for:
- Architecture design unless testability exposes a design problem.
- Broad implementation unrelated to tests.

## Workflow

1. Inspect existing test layout and commands.
2. Identify test framework and conventions.
3. Map behavior under test.
4. Choose the lowest reliable test layer.
5. Add focused tests.
6. Avoid brittle implementation assertions.
7. Run targeted tests.
8. Broaden validation when risk justifies it.

## Test Layer Rules

- Use unit tests for pure domain logic and deterministic services.
- Use integration tests for database, transactions, frameworks, and adapters.
- Use contract tests for ports, external clients, message schemas, and API compatibility.
- Use end-to-end tests sparingly for critical user journeys.
- Use characterization tests before risky refactors with unclear behavior.
- Use async test tools already present in the repo.

Choose the layer by what is changing and what reliably catches the failure:

| What changes | Cheapest reliable layer |
| --- | --- |
| Pure domain rule, deterministic service | Unit |
| Transactions, ORM, framework routes, adapters | Integration |
| Ports, external clients, message schemas, public API | Contract |
| Critical user journey | End-to-end (sparingly) |
| Under-specified behavior before a refactor | Characterization |

Use property-based tests (`hypothesis`) for invariants over ranges, and consider
mutation testing when the safety net is load-bearing. See
`references/test-patterns.md` for fixtures, factories, contract, property, and
mutation guidance, and `references/async-testing.md` for deterministic async tests.

## Quality Rules

- Test behavior, not private implementation details.
- Name tests by scenario and expected outcome.
- Keep fixtures explicit and local unless broadly reused.
- Prefer factories/builders over large fixture blobs.
- Cover failure paths, idempotency, retries, and boundaries.
- Avoid sleeps in async tests; use deterministic synchronization.
- Keep test data minimal but realistic.

## Validation

Use configured `pytest`, `tox`, `nox`, coverage, type checks, or framework commands. Start with targeted tests, then broaden when changes touch shared behavior.

Use `templates/test-plan.md` when a written test plan is useful before implementation.

## Examples

Regression coverage:
- Request: "Add a test for the duplicate webhook bug."
- Do: reproduce the bug with two identical events and assert one durable side effect.
- Watch: tests that pass without the fix, hidden clock/randomness, and database cleanup between attempts.

Integration testing:
- Request: "Test user registration with the database."
- Do: use existing database fixtures, assert committed rows and transaction behavior, and keep framework setup minimal.
- Watch: brittle global fixtures, tests depending on run order, and assertions that inspect ORM internals unnecessarily.

Async testing:
- Request: "Cover retry behavior in the async worker."
- Do: use the repo's async test plugin and deterministic fakes for queues, timers, and external clients.
- Watch: sleeps, real network calls, unawaited tasks, and event-loop leakage across tests.

## What To Watch

- Choose the cheapest test layer that can catch the failure reliably.
- A good regression test fails before the production fix.
- Prefer explicit fixture setup over magical shared state.
- Cover allow and deny paths for business rules.
- Broaden validation when shared fixtures, persistence, or public contracts are touched.

## Good / Bad

Good:
- Names tests by scenario and expected outcome.
- Uses existing fixtures, factories, and async test conventions.
- Tests observable behavior and meaningful failure paths.
- Keeps setup minimal but realistic.
- Runs the narrow test first, then broader validation when risk justifies it.

Bad:
- Tests private method choreography instead of behavior.
- Adds sleeps, real network calls, or order-dependent fixtures.
- Uses huge fixture blobs that hide the reason for the test.
- Covers only the happy path for risky business rules.
- Adds coverage that would pass even if the original bug still exists.

## Definition Of Done

Testing work is complete when:
- The behavior under test and failure mode are explicit.
- The chosen test layer is the cheapest reliable layer that catches the issue.
- Tests follow existing framework, fixture, factory, and async conventions.
- Regression tests fail on the old behavior when practical.
- Failure paths, boundaries, retries, idempotency, or compatibility are covered when relevant.
- Targeted tests were run, or the reason they could not run is stated.
