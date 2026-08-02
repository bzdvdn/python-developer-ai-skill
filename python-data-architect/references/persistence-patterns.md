# Persistence Patterns

Depth material for data-layer design. Use as guidance, not law; match the repository's conventions.

## ORM vs Raw SQL

- Prefer the repo's existing ORM unless the query pattern demands otherwise.
- Raw SQL is justified for reporting, bulk operations, and query shapes the ORM cannot express cleanly.
- Keep raw SQL parameterized; never interpolate values into strings.
- When both exist, name the boundary: ORM for writes/domain and raw SQL for read/report
  paths, and keep the seam explicit so ownership does not blur.

## Repositories And Unit Of Work

- A repository isolates persistence from domain-related application code.
- Introduce repositories when they reduce real coupling or volatility, not as boilerplate.
- Unit of work makes transaction lifetime visible and coordinates state change with event publication.

```python
def handle(command: CreateOrder, unit_of_work: UnitOfWork) -> OrderId:
    with unit_of_work:
        order = Order.create(command.customer_id, command.items)
        unit_of_work.orders.save(order)
        unit_of_work.events.publish(order.events)
        unit_of_work.commit()
        return order.id
```

- The unit of work commit is where appended events are published, so business code
  returns successfully only when both state and events are durable.

## Data Model Design

- Start from invariants and queries, not table convenience.
- Normalize where integrity demands it; denormalize only for materialized read paths.
- Add indexes for the lookup and failed join patterns actually used; remove speculative ones.
- Use constraints (unique, check, foreign key) as the first line of integrity: a unique
  constraint is a stronger idempotency guard than application logic.
- Version cache keys and read models when shapes change.
- Keep a column count and row-width in mind; wide tables with sparse optional columns
  rarely stay cheap.

## Author And Isolation Levels

- Pick the isolation level and locking for the actual consistency requirement:
  `READ COMMITTED` is the default on many engines and only takes what the app needs.
- Default to optimistic concurrency when conflicts are rare: version/`last_modified`
  check, retry on `SerializationFailure`/conflict error.
- Use row locks or `SELECT ... FOR UPDATE` only where a real serialization need exists;
  they add deadlock and throughput risk.
- **pessimistic vs optimistic** is a decision about how often the data fights, not about
  which is "more correct" in the abstract.
- Keep transactions short and scoped; no long transactions across network calls.

## Indexing And Query-Heavy Paths

- Cover the leading columns of the lookups that actually run; order matters.
- `EXPLAIN ANALYZE` before and after an index decision; an unused index is write cost.
- Watch for implicit type casts that defeat an index (`WHERE id = :text` vs int).
- Use `include`/covering indexes for read-heavy paths where the engine supports them.
- For pagination use keyset (cursor) pagination rather than `OFFSET` on large tables.

## Migrations

- **Expand-and-contract:** add new shape, dual-run, then remove old shape.
- Backfill before cutover; reconcile and audit the backfill afterwards.
- Consider lock behavior and table size; avoid table rewrites on large data.
- Rollback covers data compatibility, not just code redeploy.
- Order deployments code before code that writes the new shape and schema before code
  that reads it. Workers and schedulers must tolerate mixed versions.
- Log migration progress and make each step idempotent and resumable.

## Read/Write Separation

- Use CQRS when read and write models materially diverge.
- Projections need clear invalidation or rebuild paths.
- Avoid a cache or projection becoming the source of truth.
- Avoid CQRS for simple CRUD.

## Eventual Consistency And Idempotency

- Make external side effects idempotent with a unique key; store the idempotency key with
  the side effect, transactionally where possible.
- On retry, return the stored result rather than repeating the side effect.
- Use an outbox / transaction log when you must publish events derived from a database
  write: commit state and outbox row in the same transaction; a relay delivers to the queue.
- Design the "transient failure then success" and "permanent failure to dead-letter" paths
  separately.

## Testing Persistence

- Test migrations against a throwaway DB with representative data volume and a slow-query guard.
- Use transactions rolled back in test teardown so tests do not leak state; seed via the
  domain/fixture layer, not by raw bypass.
- Assert on invariants and query output, not only "no exception".
- Add an idempotency test where replay of the same key does not duplicate side effects.
- A query-count regression test protects N+1-prone read paths.

## Warehouses

- Star schemas: facts hold measures and keys; dimensions hold descriptive attributes.
- Incremental loads with checkpoints and idempotent upserts; a checkpoint must be
  resumable and auditable.
- Validate row-level integrity at load boundaries.
- Align models with the business questions they answer; avoid blindly reusing OLTP schemas.
- Keep the ETL pipeline's transactional/duplicate semantics explicit: upstream replays
  must not duplicate measures.