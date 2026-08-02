# Refactoring Playbook

Safe refactoring preserves behavior first, separates structural movement from semantic
change, and keeps every step reversible and independently verifiable. A refactor is a
series of small, testable steps with a defined rollback, not one big edit.

## Principles

- Preserve behavior before changing behavior.
- Add characterization tests when behavior is under-specified.
- Split structural movement from semantic changes.
- Move one boundary at a time.
- Keep public contracts stable during migration.
- Prefer incremental migration for large modules or shared APIs.
- Avoid large-bang rewrites unless the system is small, unowned, or already disposable.

## Techniques

- **Branch by abstraction:** introduce an interface, point old and new implementations
  at it, migrate callers incrementally, then remove the old path. Use when old and new
  must coexist for a long time.
- **Feature flags:** guard risky runtime behavior behind a toggle; remove the flag after
  adoption is verified. Use when the risk is runtime behavior, not structure.
- **Expand-and-contract:** for schema and API changes, add the new shape alongside the
  old, dual-run, then remove the old. Use when the change is user-visible or persisted.
- **Strangler migration:** route traffic to a new implementation incrementally while
  keeping the old one alive. Use when replacing an external boundary or subsystem.
- **Characterization tests:** pin current behavior before refactoring under-specified code.
- **Extract-and-delete / move-and-rename:** pure movement with no semantics change, kept
  as its own commit so a future `git bisect` can blame the movement commit or the
  behavior commit.

## Safety Rules

- Preserve backward compatibility for external clients and internal callers until migration completes.
- Design zero-downtime changes around compatible deploy order.
- Add observability before switching critical flows.
- Define rollback and cleanup phases before cutover.
- Remove old paths only after adoption is verified.
- Use dual-read or dual-write only with clear reconciliation.
- Each commit must compile and pass tests on its own; never land a commit that only works
  together with a later one.

## Step Sequence

1. Add characterization tests for unclear behavior.
2. Move structure without changing semantics; keep tests green at each step.
3. Introduce the abstraction or new path behind a flag or interface.
4. Migrate callers one module at a time.
5. Verify with tests, observability, and rollout checks.
6. Remove the old path and flag.
7. Update docs, ADRs, and ownership notes.

## Worked Example 1: Extract a repository from a fat service

**Evidence.** `app/application/checkout.py` is a 600-line service. `rg "Order.query|session" app/application` shows raw ORM in the service. Tests in `tests/test_checkout.py` mostly patch `Order.query`. There is no repository layer today. A second client (a Celery worker) needs the same queries.

**Reasoning.** The volatility is persistence access: it is duplicated and about to be used in a second context. That justifies a repository boundary. The first step must not change behavior, so characterize first.

1. Read the service and list every ORM touchpoint (query, session, commit, rollback). Do not refactor anything yet.
2. Add characterization tests for the query paths you will move: one test per query that asserts rows returned, ordering, and filter behavior. These must fail if behavior changes later.
3. Create `app/infrastructure/checkout_repository.py` with a class that only moves the existing SQLAlchemy calls — verbatim, same session semantics, same exception types.
4. Swap the service's internal `Order.query` calls to the repository one call-site at a time, running `pytest app/application/checkout.py` after each swap. Commit after each swap so each commit is green.
5. Once the service no longer touches the ORM directly, run the full suite and confirm the only diff is movement, not behavior.
6. Delete now-unused imports. Do not rename methods or change signatures in the same commit as the movement.

**Validation.** Full test suite green after every commit; `git diff` at step 4 shows pure call-site swaps with no assertion changes; the characterization tests still fail only if query behavior actually changes.

**Rollback.** Any single commit can be reverted independently because each is behavior-neutral. No data migration is involved, so rollback is a code-only revert.

## Worked Example 2: Rename a widely imported public API

**Evidence.** `app/reporting/aggregate.py` exports `compute_summary`, imported by 40 modules and used in a public package API that external clients import. A direct rename breaks all importers in one commit.

**Reasoning.** This is an API change, so expand-and-contract beats a rename commit: keep the old name as a thin alias during migration, then delete it once no importer uses it.

1. Add the new name and make the old name an alias: `compute_summary = compute_summary_renamed` (or a deprecated wrapper that forwards with the same signature and errors).
2. Migrate importers one package at a time, leaving the alias in place. Run tests after each package migration.
3. Grep for remaining uses of the old name: `rg "compute_summary" --glob '!tests'`. When only tests reference it, decide whether to keep a deprecated alias for external compatibility or break it in a versioned release.
4. If external clients exist, keep the alias for one deprecation cycle and log a warning; remove it in a scheduled release.

**Validation.** `pytest` green after every migration step; `rg` shows zero production uses of the old name before removal.

**Rollback.** The alias keeps old callers working, so cutting over is a two-step revert (flip importers back, keep alias).

## Worked Example 3: Remove blocking calls from an async handler

**Evidence.** `app/handlers/export.py` is an `async def export` that calls `requests.get` to a CSV endpoint and `time.sleep` between retries. `detect_async_blocking.py` flags both calls. The endpoint stalls the event loop under concurrency.

**Reasoning.** This mixes a structural change (async boundary) with a behavior change (retry timing). Split them: first make the blocking calls non-blocking without changing retry semantics, then adjust retry behavior separately.

1. Replace `requests.get` with an async HTTP client already in the dependency set (e.g. `httpx.AsyncClient`) inside the handler, preserving status handling, timeouts, and error mapping. Run the handler's tests.
2. Replace `time.sleep` in the retry loop with `await asyncio.sleep`, keeping the same backoff constants. This is a behavior-preserving swap under asyncio.
3. Only now, as a separate decision, consider backoff policy changes — and route that to the async-architect concern if it changes worker or queue topology.

**Validation.** Same tests pass with identical expected statuses and retry counts; `detect_async_blocking.py` reports no hits.

**Rollback.** Each swap is independently revertible; the handler API and response shape never change.

## Worked Example 4: Split a large orders module safely

**Evidence.** `app/orders/` contains `models.py`, `services.py`, `handlers.py`, and shared helpers in `utils.py`, 3000 lines total. `import_graph.py` shows `orders.models` imported by both `orders.services` and `billing.services`, and `orders.utils` has fan-in 25. Tests are sparse and mostly integration-level.

**Reasoning.** The module mixes three responsibilities (domain rules, orchestration, HTTP), but splitting by "pattern" without evidence will create the same tangled `utils`. Split by import clusters: which modules import `orders.services` for what reason?

1. Run `import_graph.py` and group consumers by import edge. If `billing` imports `orders.services` for the state-transition helper but not for HTTP concerns, that helper is the boundary candidate.
2. Add characterization tests for the shared helper and the state-transition path before moving anything.
3. Move the helper cluster to a new `orders/domain/` (or `orders/core/`) package — pure movement, imports updated via `rg`/find-replace, no logic change.
4. Move HTTP-only code outward to `handlers/` and orchestration to `application/`, one package at a time, keeping the old import paths working via re-export only during migration.
5. Only after movement is complete, remove any code duplicated by the split and let `import_graph.py` verify no cycle was introduced.

**Validation.** `import_graph.py` shows no new cycles and the fan-in cluster now lives inside one package; characterization tests are green before and after each move; the full suite is green at every commit.

**Rollback.** Movement commits are individually revertible; public imports are kept stable until the final cleanup commit.

## Choosing Between Techniques

| Situation | Technique |
| --- | --- |
| Long coexistence of old and new implementation | Branch by abstraction |
| Risky runtime behavior change | Feature flag |
| Schema or public API change | Expand-and-contract |
| Replacing an external boundary or subsystem | Strangler |
| Under-specified behavior before touching it | Characterization tests |
| Pure movement, no semantics change | Extract-and-delete / move-and-rename |

## Common Failure Modes

- Moving structure and changing behavior in the same commit, then blaming tests for "failing to keep up".
- Adding characterization tests that already encode the buggy behavior as truth instead of current behavior.
- Introducing an abstraction before any concrete pressure exists, then having to migrate callers twice.
- Removing the old path before adoption is verified, stranding a client on a deleted API.
- Refactoring `utils.py` last because it is "just helpers", then discovering it is the real architecture.
- Letting a refactor silently change public signatures, exception types, or response shapes.
