# Evals: python-coder

## Scenario: coder-bugfix-idempotent

### Prompt
Fix duplicate invoice creation when the webhook handler retries.

### Repository Fixture
```
app/handlers/webhooks.py  -> on event, creates invoice unconditionally
app/application/invoices.py -> create_invoice(db, payload)
tests/test_webhooks.py    -> one happy-path test
app/models.py             -> Invoice with no unique constraint
```

### Expected Behavior
- Inspects the handler, the creation path, and existing tests before editing.
- Adds the smallest guard (idempotency key + unique constraint or lookup) that preserves API behavior.
- Adds or updates a regression test that replays the same event.
- Reports changed behavior, files, tests, and residual risk.

### Acceptance Criteria
- [ ] Change is minimal and behavior-preserving.
- [ ] A regression test proves the second delivery creates no duplicate.
- [ ] Report names files touched and validation commands run.

### Anti-Criteria
- [ ] Rewrites surrounding architecture while fixing the bug.
- [ ] Introduces a new framework or library without precedent.
- [ ] Claims validation passed without running it.

## Scenario: coder-implement-plan

### Prompt
Implement the billing port and Stripe adapter from this plan (phase 2 only).

### Repository Fixture
```
app/domain/billing.py    -> Subscription + BillingProvider Protocol (stub)
app/application/billing.py -> BillingService expecting the provider
app/infrastructure/      -> empty
tests/test_billing.py    -> fakes provided
plan excerpt: add StripeBillingProvider implementing BillingProvider; keep domain free of Stripe types.
```

### Expected Behavior
- Follows the plan's named files, contracts, and phase scope.
- Implements the adapter without leaking Stripe exceptions/types into domain.
- Reuses existing fakes; runs targeted tests.

### Acceptance Criteria
- [ ] `StripeBillingProvider` satisfies the `Protocol` and maps Stripe payloads at the boundary.
- [ ] Domain files unchanged.
- [ ] Targeted tests pass.

### Anti-Criteria
- [ ] Changes domain contracts not in the plan.
- [ ] Introduces provider SDK types into `app/application`.
- [ ] Implements phases beyond the assigned scope.

## Scenario: coder-refactor-email

### Prompt
Move email sending out of the FastAPI route into an application service.

### Repository Fixture
```
app/handlers/register.py  -> sends email inline after creating user
app/application/          -> empty
tests/test_register.py    -> asserts response JSON
```

### Expected Behavior
- Introduces or reuses an application service; keeps the route behavior stable.
- Keeps response shape identical.
- Adds tests around the service behavior.

### Acceptance Criteria
- [ ] Route response shape unchanged (test still green).
- [ ] Email sending logic lives in the service with dependencies injected.
- [ ] No unrelated formatting churn.

### Anti-Criteria
- [ ] Changes response shape or validation behavior.
- [ ] Reorganizes unrelated files.
