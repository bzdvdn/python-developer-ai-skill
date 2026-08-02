# Evals: python-testing

## Scenario: testing-regression-webhook

### Prompt
Add a regression test for the duplicate webhook bug.

### Repository Fixture
```
app/handlers/webhooks.py  -> creates invoice per event, no idempotency
app/application/invoices.py
tests/test_webhooks.py    -> one happy-path test
conftest.py               -> sqlite in-memory fixture
```

### Expected Behavior
- Reproduces the bug: two identical events, one durable side effect.
- Asserts observable behavior (row count/committed state), not mock choreography.
- Uses existing fixtures; keeps setup minimal.
- Test fails on the old behavior.

### Acceptance Criteria
- [ ] Test sends the same event twice and asserts a single durable invoice.
- [ ] Test fails before the fix.
- [ ] Uses existing fixture/factory conventions.

### Anti-Criteria
- [ ] Tests private method choreography.
- [ ] Uses sleeps or real network calls.
- [ ] Passes even when the bug still exists.

## Scenario: testing-layer-choice

### Prompt
How should I test the order checkout flow?

### Repository Fixture
```
app/domain/orders.py     -> Order.create, apply_discount (pure)
app/application/checkout.py -> orchestrates payment provider + repo
app/infrastructure/payments.py -> HTTP client to provider
tests/                   -> route-level tests only
```

### Expected Behavior
- Recommends the cheapest reliable layer per behavior: unit for domain rules,
  integration for the service with fakes, contract for the payment adapter.
- Explains why route-level-only coverage is insufficient for business rules.

### Acceptance Criteria
- [ ] Differentiates unit vs integration vs contract layers.
- [ ] Recommends fakes for the payment provider at the service layer.
- [ ] Justifies the choice in terms of cost and failure catch.

### Anti-Criteria
- [ ] Recommends e2e tests for pure domain logic.
- [ ] Ignores the domain layer entirely.

## Scenario: testing-async-worker

### Prompt
Cover retry behavior in the async worker without flakiness.

### Repository Fixture
```
app/workers/consumer.py  -> async handler with retry on transient errors
tests/test_consumer.py   -> pytest-asyncio configured
```

### Expected Behavior
- Uses deterministic fakes for the queue/timer; no real `asyncio.sleep`.
- Covers success, transient failure then success, and permanent failure.
- Avoids event-loop leakage between tests.

### Acceptance Criteria
- [ ] No sleeps; synchronization is deterministic.
- [ ] Retry scenarios (transient, permanent) covered.
- [ ] Uses the repo's async test plugin.

### Anti-Criteria
- [ ] Introduces `time.sleep` or real network calls.
- [ ] Leaves unawaited tasks leaking across tests.
