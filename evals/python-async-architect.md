# Evals: python-async-architect

## Scenario: async-worker-design

### Prompt
Design the invoice-generation worker.

### Repository Fixture
```
app/domain/invoices.py -> Invoice.create, idempotency_key field
app/application/billing.py -> generate_invoice flow
app/infrastructure/queue.py -> existing broker setup
```

### Expected Behavior
- Designs queue topology, prefetch, concurrency limit, idempotency key, bounded retries with backoff, DLQ, and metrics.
- Keeps delivery semantics at-least-once with idempotent handlers.

### Acceptance Criteria
- [ ] Idempotency key used transactionally with the side effect.
- [ ] Retries bounded with backoff; DLQ explicit.
- [ ] Backpressure and concurrency limits designed.
- [ ] Observability covers queue depth, lag, retries, DLQ.

### Anti-Criteria
- [ ] Ignores at-least-once semantics (duplicates possible).
- [ ] Unbounded retries or no DLQ.
- [ ] Blocking calls in the worker design.

## Scenario: async-migration

### Prompt
Move the checkout flow from sync Flask to async.

### Repository Fixture
```
app/handlers/checkout.py -> sync, calls requests and sync SQLAlchemy session
```

### Expected Behavior
- Identifies blocking calls, chooses async clients/drivers.
- Plans migration outward-in with flags or branch by abstraction.
- Keeps behavior and transaction semantics identical.

### Acceptance Criteria
- [ ] Flags blocking calls with paths.
- [ ] Migration is phased and reversible.
- [ ] Tests are the safety net for behavior preservation.

### Anti-Criteria
- [ ] Mixes blocking and async in the same call path.
- [ ] Uses async for effect without a workload justification.

## Scenario: async-backpressure

### Prompt
The queue backlog is taking down consumers.

### Repository Fixture
```
worker.py -> infinite retry loop, no DLQ, no concurrency limit
monitoring -> no queue-depth metric
```

### Expected Behavior
- Inspects retry behavior, prefetch, concurrency, DLQ, metrics.
- Designs bounded backpressure and monitoring.

### Acceptance Criteria
- [ ] Identifies unbounded retries and missing backpressure.
- [ ] Recommends concurrency limits, DLQ, and queue-depth alerting.

### Anti-Criteria
- [ ] Fixes symptoms only (restart workers).
