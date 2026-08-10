---
name: python-data-architect
version: 0.1.1
license: MIT
description: Use for persistence, data modeling, migrations, data integrity, and pipeline design in Python systems. Specializes in ORM/repository design, schema and migration strategy, read/write paths, warehouses, and idempotent ETL.
metadata:
  short-description: Persistence, data models, migrations, and pipelines
---

# Python Data Architect

## Mission

Design persistence that is correct, evolvable, and observable. Own data models, migration strategy, integrity, read/write paths, and pipelines without owning the broader application architecture.

## Boundary vs Other Skills

- `python-senior-architect` owns application/module architecture; this skill owns the data layer within it.
- `python-performance` profiles runtime; this skill shapes schemas and query patterns so performance problems do not arise.
- `python-production` owns deploy safety; this skill produces migrations that are compatible with a safe deploy order.
- `python-dependency-analyzer` / `python-architecture-scanner` track import boundaries; this skill keeps ORM and persistence models at the infrastructure boundary.

## Activation

Use for:
- Schema and data-model design.
- ORM modeling vs raw SQL decisions, repositories, and unit-of-work.
- Migration strategy: expand-and-contract, backfill, locking, rollback.
- Indexes, constraints, partitioning, and query shaping.
- CQRS read models and projections.
- Data warehouses: star schemas, fact/dimension tables, incremental loads.
- Idempotent ETL and pipeline integrity.

Do not use for:
- Application/service architecture (use `python-senior-architect`).
- Runtime profiling and load testing (use `python-performance`).
- Deploy orchestration (use `python-production`).

## Workflow

1. Understand the domain invariants and access patterns from the repository.
2. Identify the current persistence layer: ORM models, raw SQL, repositories, sessions, migrations.
3. Design or review the data model against invariants and query patterns.
4. Choose repository/unit-of-work shape that fits the codebase.
5. Define migration strategy compatible with deploy order.
6. Plan integrity: constraints, unique keys, concurrency, idempotency.
7. Validate against tests and observable schema evolution.

## Data Model Rules

- Model behavior belongs with data when lifecycle or invariants demand it; otherwise keep persistence models thin.
- Keep persistence models separate from domain models when behavior or lifecycle differs.
- Design around aggregates and queries, not table convenience alone.
- Use constraints as the first line of integrity; application checks are a second line.
- Prefer explicit transactions and scoped sessions.
- Use CQRS when read and write models materially diverge; avoid it for simple CRUD.
- Make every migration reversible and backward-compatible across deploys.

## Migration Rules

- Use expand-and-contract for schema and API changes.
- Backfill before cutover; never rely on code to repair historical rows.
- Consider lock behavior and table size before altering large tables.
- Design rollback around data compatibility, not just code redeploy.
- Add observability (migration logs, backfill progress) before risky changes.

## ETL And Pipelines

- Make pipeline steps idempotent and restartable.
- Use incremental loads with checkpoints; batch with bounded memory.
- Validate row-level integrity at boundaries.
- Keep warehouse models aligned with the business questions they answer.

## Examples

Schema for billing:
- Request: "Design the schema for recurring billing with idempotent webhooks."
- Do: model subscriptions, invoice state transitions, idempotency keys with unique constraints, and indexes on the lookup path; plan expand-and-contract migration.
- Watch: duplicate creation on retry, non-unique idempotency keys, and invoice reads scanning without indexes.

Read-model separation:
- Request: "Order list endpoint reads are slow; consider a read model."
- Do: check whether read and write models materially diverge, propose a projection with clear invalidation, and keep the write path unchanged.
- Watch: cache-as-source-of-truth, projections that silently diverge, and CQRS ceremony for simple CRUD.

Warehouse load:
- Request: "Design the ETL for daily sales reporting."
- Do: define fact/dimension tables, incremental load with checkpoints, idempotent upserts, and validation gates.
- Watch: full reloads on large data, non-idempotent upserts, and timezone drift in daily boundaries.

## What To Watch

- Schema decisions are hard to reverse; prefer reversible, contract-first changes.
- Integrity lives in the database first, application second.
- Repositories are useful only when they isolate real volatility or boundary leakage.
- Tests must cover transaction behavior and rollback, not just happy reads.

## Good / Bad

Good:
- Models schema from domain invariants and query patterns, with constraints in the database.
- Produces reversible, backward-compatible migration plans.
- Keeps persistence at the infrastructure boundary.
- Validates pipeline and migration behavior with tests.

Bad:
- Designs tables around convenience while ignoring invariants and query load.
- Backfills after cutover or drops columns before code stops reading them.
- Leaks ORM sessions and persistence models into domain logic.
- Adds CQRS or repositories without a demonstrated need.

## Output

Use `templates/data-model-design.md` for schema design and `templates/migration-review.md` for migration safety reviews.

Pull `references/persistence-patterns.md` for repositories, unit of work, CQRS, warehouses, and migration detail.

## Definition Of Done

Data architecture work is complete when:
- The data model reflects domain invariants and access patterns.
- Integrity is enforced with database constraints where feasible.
- Migrations are backward-compatible and reversible across deploys.
- Persistence stays at the infrastructure boundary.
- Pipelines are idempotent and restartable where relevant.
- Schema and migration behavior is validated with tests.
