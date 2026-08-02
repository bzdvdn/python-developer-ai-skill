# Evals: python-dependency-analyzer

## Scenario: dependency-circular-import

### Prompt
Find why importing the app fails with a circular import.

### Repository Fixture
```
app/domain/orders.py -> imports settings from app/config
app/config.py -> imports from app/domain/orders (for defaults)
app/__init__.py -> imports config at package load
```

### Expected Behavior
- Locates the concrete import chain (orders -> config -> orders) with paths.
- Separates runtime imports from type-only imports.
- Identifies the smallest boundary fix and flags `__init__.py` side effects.

### Acceptance Criteria
- [ ] Reports the concrete cycle path, not just module names.
- [ ] Points to the import-time side effect as the likely cause.
- [ ] Suggests moving dependency direction, not hiding the import in a function.

### Anti-Criteria
- [ ] Says "circular dependency" without the import chain.
- [ ] Fixes by moving imports into functions without addressing boundary design.

## Scenario: dependency-layer-violation

### Prompt
Check whether domain imports infrastructure.

### Repository Fixture
```
app/domain/orders.py -> imports sqlalchemy.orm.Session and httpx
app/infrastructure/ -> repository uses sqlalchemy
pyproject.toml -> sqlalchemy, httpx
```

### Expected Behavior
- Defines first-party package roots and expected layers from evidence.
- Reports concrete offending edges (file -> imported symbol).
- Separates production imports from type-only/test imports.

### Acceptance Criteria
- [ ] Identifies domain importing sqlalchemy/httpx with concrete paths.
- [ ] States the expected layer rule it references.

### Anti-Criteria
- [ ] Declares layer violations before defining layers.
- [ ] Mixes stdlib/third-party/first-party/test imports in one list.

## Scenario: dependency-sprawl

### Prompt
Explain dependency sprawl in this service.

### Repository Fixture
```
pyproject.toml -> httpx + requests + aiohttp + urllib3 all present; unused package `boto3`
```

### Expected Behavior
- Groups dependencies by purpose, identifies overlap and unused packages.
- Distinguishes dependency-health issues from architecture issues.

### Acceptance Criteria
- [ ] Flags overlapping HTTP clients and the unused dependency.
- [ ] Distinguishes health vs boundary concerns.

### Anti-Criteria
- [ ] Recommends package reshuffles without considering public import compatibility.
