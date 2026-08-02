# Evals: python-performance

## Scenario: performance-slow-endpoint

### Prompt
The order list endpoint is slow.

### Repository Fixture
```
app/handlers/orders.py -> returns all orders, serializes in a loop
app/application/orders.py -> N+1: fetches order then items per row
tests/ -> none for performance
```

### Expected Behavior
- Defines the symptom and target before optimizing.
- Locates N+1 and unbounded result set with code evidence.
- Proposes the smallest behavior-preserving fix and a way to notice regression.

### Acceptance Criteria
- [ ] Identifies N+1 and unbounded result set as confirmed risks.
- [ ] Separates measurement from hypothesis.
- [ ] Recommends pagination/join + a regression benchmark or query-count test.

### Anti-Criteria
- [ ] Guesses the bottleneck from style alone.
- [ ] Adds caching without addressing freshness/invalidation.
- [ ] Changes response semantics for speed without saying so.

## Scenario: performance-async-blocking

### Prompt
FastAPI gets slower under concurrent requests.

### Repository Fixture
```
app/handlers/orders.py -> async def handler uses `requests.get` (blocking)
app/db.py -> sync SQLAlchemy session used in async handlers
```

### Expected Behavior
- Flags blocking `requests` in async code and sync DB access on the event loop.
- Checks connection pool limits and timeouts.

### Acceptance Criteria
- [ ] Flags blocking I/O in async handlers with path.
- [ ] Recommends async client/async DB driver and timeouts.

### Anti-Criteria
- [ ] Optimizes cold paths while ignoring network/database costs.
- [ ] Reports improvement without a baseline or validation method.

## Scenario: performance-memory

### Prompt
Worker memory climbs during large imports.

### Repository Fixture
```
app/workers/importer.py -> reads entire file into a list, processes in loop, retains rows
```

### Expected Behavior
- Inspects loops, batching, retained collections, streaming.
- Flags full-file load and unbounded retention.

### Acceptance Criteria
- [ ] Flags loading the entire file into memory.
- [ ] Recommends streaming/batching with a bound.

### Anti-Criteria
- [ ] Suggests cache "fix" that ignores memory growth.
