# Evals: python-senior-architect

## Scenario: architect-review-clean-architecture

### Prompt
Does this FastAPI service follow clean architecture?

### Repository Fixture
```
app/handlers/orders.py        -> @router.post uses OrderService (thin)
app/application/orders.py     -> OrderService calls OrderRepository Protocol
app/domain/orders.py          -> Order aggregate, no external imports
app/infrastructure/orders.py  -> SqlAlchemyOrderRepository (imports sqlalchemy)
app/models.py                 -> ORM rows
tests/test_orders.py          -> unit tests on domain; one route test
pyproject.toml                -> fastapi, sqlalchemy, pydantic
```

### Expected Behavior
- Inspects handlers, application, domain, infrastructure, models, tests before judging.
- States that handlers and ORM live at boundaries; domain is framework-free.
- Flags the ORM rows in `app/models.py` shared as domain objects as a boundary leak.
- Gives a verdict with evidence paths, not labels alone.

### Acceptance Criteria
- [ ] Verdict references at least three distinct files as evidence.
- [ ] Distinguishes facts (imports) from inferences (style).
- [ ] Identifies at least one real boundary issue with a concrete path.
- [ ] Produces recommendations ordered by impact, with migration step.

### Anti-Criteria
- [ ] Declares "clean architecture" or "not clean" without file evidence.
- [ ] Prescribes DDD/Hexagonal because the terms sound senior.
- [ ] Writes large implementation patches.

## Scenario: architect-plan-billing

### Prompt
Plan how to add recurring billing without coupling it to the FastAPI handlers or Stripe.

### Repository Fixture
```
app/handlers/checkout.py  -> inline calls to stripe in the route
app/domain/               -> empty
app/application/          -> one service, no ports
app/infrastructure/       -> db.py only
```

### Expected Behavior
- Produces a phased implementation plan: domain, port, adapter, webhook boundary.
- Names affected modules, required abstractions, tests per phase, migration, risks.
- Keeps provider types out of the domain.
- Includes delegation notes specific enough for a Coder.

### Acceptance Criteria
- [ ] Plan has phases, each reversible and independently testable.
- [ ] A provider `Port` and `Stripe` adapter are explicit.
- [ ] Idempotency and webhook trust are addressed.
- [ ] Delegation notes name files and out-of-scope areas.

### Anti-Criteria
- [ ] Writes the implementation code itself.
- [ ] Lets provider payloads cross into domain in the plan.

## Scenario: architect-pr-review

### Prompt
Review this PR for architectural risks. The PR adds a cache in front of order reads.

### Repository Fixture
```
app/application/orders.py  -> service now reads from redis cache, falls back to DB
app/infrastructure/cache.py -> new, redis client
tests/test_orders.py        -> tests updated to assert cache hits
diff: service changes ~40 lines
```

### Expected Behavior
- Reviews the diff plus surrounding code and tests.
- Flags cache invalidation semantics, source-of-truth concerns, and key design.
- Notes whether the cache lives at the right boundary.
- States migration/rollback safety if behavior changes.

### Acceptance Criteria
- [ ] Blocking vs non-blocking findings separated.
- [ ] Cache invalidation and observability addressed with evidence.
- [ ] Verdict references the changed files.

### Anti-Criteria
- [ ] Approves cache without questioning invalidation.
- [ ] Reviews unrelated code instead of the diff.
