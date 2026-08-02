# Evals: python-architecture-scanner

## Scenario: scanner-ci-gate

### Prompt
Gate CI so domain never imports infrastructure.

### Repository Fixture
```
app/domain/orders.py       -> imports sqlalchemy.orm.Session and httpx
app/application/checkout.py -> imports app.handlers.api
app/handlers/api.py
contract.json               -> layers domain/application/handlers; forbidden domain->infra, application->handlers
```

### Expected Behavior
- Defines layers from package roots.
- Produces a machine-checkable contract and runs the check.
- Reports concrete import edges for every violation.
- Recommends wiring the check into CI.

### Acceptance Criteria
- [ ] Violations reported with file paths and target imports.
- [ ] Distinguishes layer matches from keyword-category matches.
- [ ] Recommends a CI/PR gate and remediation.

### Anti-Criteria
- [ ] Codifies a rule the repo does not intend to follow.
- [ ] Reports violations without the import chain.
- [ ] Relaxes the contract to hide a real cycle.

## Scenario: scanner-drift

### Prompt
Produce a package-metrics and drift report for the repo.

### Repository Fixture
```
app/domain, app/application, app/infrastructure
documented layer contract (architecture-contract.md) allowing domain->application only
actual imports: domain -> infrastructure (httpx)
```

### Expected Behavior
- Runs deterministic scans and summarizes metrics.
- Compares actual imports against the documented contract.
- Reports drift edges with file references.

### Acceptance Criteria
- [ ] Metrics are summarized (modules, edges, cycles where applicable).
- [ ] Drift edges reference concrete files.
- [ ] Distinguishes production from test-only imports.

### Anti-Criteria
- [ ] Metrics without an intended target or contract.
