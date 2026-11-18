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

## Scenario: coder-no-global-or-cast

### Prompt
Add a discount lookup to the pricing service. Reuse the existing cache and settings.

### Repository Fixture
```
app/cache.py            -> module-level CACHE dict mutated through global statements
app/services/pricing.py -> PriceService(settings, cache) already takes dependencies
app/domain/discounts.py -> DiscountRules Protocol + validated from_payload() helper
tests/test_pricing.py   -> fakes for settings and cache
```

### Expected Behavior
- Inspects the service constructor, cache API, and existing fakes before editing.
- Passes the cache/settings through the existing dependencies instead of adding `global`.
- Parses untrusted payloads with the validated helper or explicit narrowing instead of `cast`/`# type: ignore`.
- Adds a regression test for the new lookup using the existing fakes.

### Acceptance Criteria
- [ ] No new `global` statement or module-level mutable state.
- [ ] No new `typing.cast`, `# type: ignore`, or `Any` widening to silence the checker.
- [ ] New behavior is covered by a test using injected fakes.

### Anti-Criteria
- [ ] Adds `global CACHE` (or similar) so the service can reach module state.
- [ ] Uses `cast(...)` or a type-ignore comment instead of fixing the type flow.
- [ ] Edits unrelated modules or reformats the repository.
