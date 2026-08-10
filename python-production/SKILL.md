---
name: python-production
version: 0.1.1
license: MIT
description: Use for Python production readiness, deployment architecture, observability, configuration, migrations, rollback, incidents, runbooks, SLOs, background workers, and operational safety.
metadata:
  short-description: Prepare Python systems for production
---

# Python Production

## Mission

Make Python systems operable, observable, deployable, and recoverable. Treat production behavior as part of the design.

## Activation

Use for:
- Production readiness review.
- Deployment and rollback planning.
- Observability design.
- Incident analysis.
- Runtime configuration.
- Database migration safety.
- Worker and scheduler operations.
- SLOs, alerts, and runbooks.

## Workflow

1. Identify runtime components.
2. Inspect deployment, config, migrations, workers, and docs.
3. Map startup, shutdown, health checks, and dependencies.
4. Review logs, metrics, traces, alerts, and dashboards.
5. Review deploy order, rollback, and data compatibility.
6. Produce readiness gaps and rollout plan.

## Checklist

- Config is explicit, validated, and environment-aware.
- Secrets are injected safely.
- Health checks reflect real dependencies.
- Startup and shutdown are graceful.
- Migrations are backward-compatible across deploys.
- Rollback plan exists and is tested where feasible.
- Logs are structured and include correlation IDs.
- Metrics cover latency, errors, throughput, saturation, and business health.
- Traces cross service and queue boundaries.
- Alerts map to user impact.
- Workers are idempotent and retry-safe.
- Runbooks explain common failure modes.
- Capacity and scaling assumptions are documented.

## Examples

Production readiness:
- Request: "Prepare this FastAPI service for launch."
- Do: inspect startup/shutdown, config validation, health checks, migrations, logs, metrics, alerts, deployment files, and rollback path.
- Watch: health checks that only return process liveness, missing timeouts, unvalidated env vars, and migrations that cannot roll back safely.

Migration rollout:
- Request: "Review this database migration for deploy safety."
- Do: check expand-and-contract order, backward compatibility with old and new code, lock behavior, data backfill, and rollback.
- Watch: table rewrites on large data, dropping columns before code cutover, and workers reading mixed schema versions.

Incident analysis:
- Request: "Analyze why the queue backlog took down checkout."
- Do: map timeline, saturation signals, retry behavior, dead-letter handling, alerts, runbooks, and user impact.
- Watch: unbounded retries, missing backpressure, noisy alerts, and remediation that only patches symptoms.

## What To Watch

- Production readiness is about recovery and diagnosis as much as deployment.
- Rollback plans must include data compatibility, not just code redeploy.
- Logs, metrics, traces, and alerts should map to user-impacting failure modes.
- Workers need idempotency, retry limits, and operational controls.
- State unknowns clearly when deployment or dashboard evidence is unavailable.

## Good / Bad

Good:
- Maps runtime components, dependencies, deploy order, and rollback path.
- Reviews config, secrets, health checks, migrations, workers, and observability together.
- Connects alerts and runbooks to concrete user-impacting failures.
- Calls out data compatibility and mixed-version behavior during deploys.
- Produces an actionable readiness gap list with owners or next steps when useful.

Bad:
- Treats "service starts locally" as production readiness.
- Designs rollback as code redeploy while ignoring migrated data.
- Adds logs without correlation IDs or useful operational context.
- Creates alerts on noisy internals instead of user impact.
- Ignores workers, schedulers, queues, or background side effects.

## Output Templates

Use `templates/production-readiness.md` for production readiness reviews when a reusable report file is helpful. The template covers runtime components, dependencies, readiness gaps, deployment risks, migration and rollback, observability gaps, required tests, recommendations, and unknowns.

For incident analysis, structure output as: Summary, Timeline, User Impact, Technical Contributors, Detection Gaps, Recovery Gaps, Remediation, Follow-Up Ownership.

Pull `references/production-playbook.md` for deploy safety, health checks, observability, runbooks, and incident response detail.

## Definition Of Done

Production work is complete when:
- Runtime components, dependencies, deploy order, and rollback path are mapped.
- Config, secrets, health checks, startup, shutdown, migrations, workers, and schedulers are reviewed when in scope.
- Observability gaps cover logs, metrics, traces, alerts, dashboards, and runbooks where evidence exists.
- Migration and rollback recommendations account for mixed-version code and data compatibility.
- Readiness gaps are prioritized by user impact and recovery risk.
- Unknown deployment facts are stated instead of assumed.
