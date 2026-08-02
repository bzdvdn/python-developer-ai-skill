# Evals: python-production

## Scenario: production-readiness

### Prompt
Prepare this FastAPI service for launch.

### Repository Fixture
```
app/main.py -> uvicorn app; no startup/shutdown hooks
app/config.py -> reads env vars without validation
app/health.py -> returns {"ok": true} without dependency checks
app/db.py -> migrations folder exists, no rollback notes
docker-compose.yml, no observability config
```

### Expected Behavior
- Inspects startup/shutdown, config validation, health checks, migrations, logs, metrics, alerts, deploy files.
- Flags unvalidated env vars, liveness-only health checks, missing rollback notes.
- Produces a prioritized readiness gap list.

### Acceptance Criteria
- [ ] Flags config without validation and health check that ignores dependencies.
- [ ] Covers migrations and rollback path.
- [ ] Output maps gaps to user impact.

### Anti-Criteria
- [ ] Treats "service starts locally" as production readiness.
- [ ] Designs rollback as code redeploy ignoring migrated data.

## Scenario: production-migration-rollout

### Prompt
Review this database migration for deploy safety.

### Repository Fixture
```
migrations/002_drop_legacy_column.sql -> drops column with large table
app code still reads legacy column for one version
```

### Expected Behavior
- Checks expand-and-contract order, backward compatibility with old and new code,
  lock behavior, backfill, and rollback.
- Flags dropping a column before code cutover.

### Acceptance Criteria
- [ ] Flags the drop-before-cutover risk with file reference.
- [ ] Recommends expand-and-contract order and rollback.

### Anti-Criteria
- [ ] Ignores mixed-version code behavior during deploys.

## Scenario: production-incident

### Prompt
Analyze why the queue backlog took down checkout.

### Repository Fixture
```
worker.py -> unbounded retry loop, no dead-letter handling, no backpressure
monitoring -> no queue-depth alert
```

### Expected Behavior
- Maps timeline, saturation signals, retry behavior, DLQ handling, alerts, runbooks.
- Flags unbounded retries and missing backpressure as contributors.

### Acceptance Criteria
- [ ] Identifies unbounded retries and missing alerting as contributors.
- [ ] Connects detection gaps to user impact.

### Anti-Criteria
- [ ] Recommends remediation that only patches symptoms.
