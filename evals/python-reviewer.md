# Evals: python-reviewer

## Scenario: reviewer-correctness

### Prompt
Review this PR that changes order cancellation.

### Repository Fixture
```
diff in app/application/orders.py  -> cancel() now skips refund when order is refunded
tests/test_orders.py               -> updated for one path
```

### Expected Behavior
- Inspects the diff, caller expectations, state transitions, and tests.
- Flags new invalid states (cancelled-from-shipped), non-idempotent retries,
  partial commits, and missing edge-case regression tests.
- Prioritizes findings by severity with file references.

### Acceptance Criteria
- [ ] Blocking findings listed first with `path:line` references.
- [ ] Distinguishes blockers from suggestions.
- [ ] Mentions missing tests for edge cases.
- [ ] Says explicitly if no findings; names residual risk.

### Anti-Criteria
- [ ] Leads with praise and buries findings.
- [ ] Reports style preferences as defects.
- [ ] Invents risk not supported by the diff.

## Scenario: reviewer-api-compat

### Prompt
Review this response schema change.

### Repository Fixture
```
diff: renaming field `amount` -> `total` in UserResponse, OpenAPI updated
clients/ -> one client reading `amount`
```

### Expected Behavior
- Compares old and new contracts, serialization, clients, and migration notes.
- Flags renamed fields, nullability changes, error-shape drift, breaking clients.

### Acceptance Criteria
- [ ] Identifies the breaking client change with a file reference.
- [ ] Notes versioning or compatibility options.

### Anti-Criteria
- [ ] Approves schema change without checking consumers.
- [ ] Flags speculative issues without diff evidence.

## Scenario: reviewer-test-review

### Prompt
Review these new tests.

### Repository Fixture
```
tests/test_orders.py  -> mocks assert internal call order; fixtures hide setup
```

### Expected Behavior
- Checks whether tests fail on the old bug, cover the right layer, and avoid
  coupling to private implementation.
- Calls out mock-choreography assertions and fixture blobs.

### Acceptance Criteria
- [ ] Flags tests that assert implementation choreography.
- [ ] Flags fixtures that hide important setup.
- [ ] Notes missing negative cases.

### Anti-Criteria
- [ ] Approves coverage that would pass despite the bug.
