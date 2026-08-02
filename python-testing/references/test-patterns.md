# Test Patterns Reference

Use as style guidance, not universal law. Prefer existing repository conventions.

## Choosing The Layer

| What changes | Cheapest reliable layer |
| --- | --- |
| Pure domain rule, deterministic service | Unit |
| Transactions, ORM, framework routes, adapters | Integration |
| Ports, external clients, message schemas, public API | Contract |
| Critical user journey across processes | End-to-end (sparingly) |
| Under-specified behavior before a risky refactor | Characterization |

Rule: pick the layer that reliably catches the failure at the lowest cost. A test that
needs a database to test a pure rule is over-expensive; a unit test that fakes a
database for a transaction is under-reliable.

## Fixtures And Factories

- Keep fixtures explicit and local unless broadly reused.
- Prefer factories/builders over large fixture blobs that hide important setup.
- Fakes implement the same interface as the real dependency and fail loudly when
  exercised in unsupported ways.
- Make test data minimal but realistic; a row should contain only fields the test cares about.

Example factory:

```python
def make_order(**overrides: object) -> Order:
    data = {"id": "ord_1", "customer_id": "cus_1", "status": "pending", "items": []}
    data.update(overrides)
    return Order(**data)
```

## Isolation And Determinism

- No order-dependent tests; each test sets up its own state.
- No sleeps; use deterministic synchronization in async tests.
- No real network calls in unit tests.
- Freeze clocks (`freezegun`) and inject ID generators instead of reading `datetime.now()` inline.
- Clean up database state between tests via the repo's transaction/rollback convention.

## Failure Path Coverage

- Cover allow and deny paths for business rules.
- Cover retries, idempotency, timeouts, and boundary values.
- A regression test should fail before the production fix.

## Contract Testing

- Verify adapter/port agreement without depending on the external system.
- Record provider responses as fixtures and assert the adapter maps them correctly.
- Include schema drift detection (OpenAPI/JSON Schema) for public contracts.

## Property-Based Testing

- Generate inputs with `hypothesis` when invariants hold over ranges (parsers,
  serializers, pricing math, sorting).
- Always pair property tests with concrete examples for readability.

## Mutation Testing

- Use a mutation tool (for example `mutmut`) when the safety net is load-bearing.
- Treat surviving mutations on domain invariants as evidence of a test gap, not an
  automatic blocker.

## Anti-Patterns

- Tests that only assert mocks were called (choreography, not behavior).
- Fixture blobs hiding the reason for the test.
- Coverage without assertion quality (tests that pass even when the bug exists).
- Tests coupled to private method names and internal call order.
