# Evals: python-data-architect

## Scenario: data-schema-billing

### Prompt
Design the schema for recurring billing with idempotent webhooks.

### Repository Fixture
```
app/domain/ -> no billing domain yet
app/infrastructure/db.py -> SQLAlchemy setup
```

### Expected Behavior
- Models subscriptions, invoices, and state transitions.
- Uses a unique idempotency key and indexes on the lookup path.
- Plans an expand-and-contract migration.

### Acceptance Criteria
- [ ] Idempotency enforced with a unique constraint, not only application checks.
- [ ] Migration is backward-compatible and reversible.
- [ ] Integrity (state transitions, foreign keys) is in the schema.

### Anti-Criteria
- [ ] Backfills after cutover.
- [ ] Leaks ORM sessions into domain logic.
- [ ] Adds CQRS for a simple CRUD shape.

## Scenario: data-read-model

### Prompt
Order list reads are slow; should we introduce a read model?

### Repository Fixture
```
app/application/orders.py -> reads orders + items per request (N+1)
app/domain/orders.py       -> write model
```

### Expected Behavior
- Checks whether read and write models materially diverge.
- Proposes a projection with clear invalidation or rebuild path.
- Keeps the write path unchanged.

### Acceptance Criteria
- [ ] Justifies read-model decision from access patterns.
- [ ] Invalidation/rebuild semantics are explicit.
- [ ] Avoids CQRS ceremony if unnecessary.

### Anti-Criteria
- [ ] Uses cache or projection as source of truth.
- [ ] Recommends CQRS without a demonstrated divergence.

## Scenario: data-migration-review

### Prompt
Review this migration for deploy safety.

### Repository Fixture
```
migrations/002_drop_legacy.sql -> drops a column while old code still reads it
migrations/003_backfill.sql    -> backfill runs after cutover
```

### Expected Behavior
- Flags drop-before-cutover and backfill-after-cutover risks.
- Recommends expand-and-contract order and rollback.

### Acceptance Criteria
- [ ] Identifies both deploy-order risks with references.
- [ ] Rollback covers data compatibility.

### Anti-Criteria
- [ ] Ignores lock behavior or table size on a large table.
