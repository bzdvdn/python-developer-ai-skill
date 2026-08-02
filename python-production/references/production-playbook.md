# Production Playbook

Operability reference: deployment, observability, migrations, and incidents.

## Deploy Safety

- Deploy order must respect mixed-version compatibility: schema before code that
  reads it, code before code that writes the new shape.
- Use expand-and-contract for schema and API changes.
- Rollback plan covers data compatibility, not just code redeploy.
- Workers, schedulers, and web processes must tolerate mixed schema versions.
- Make deploys reproducible from the lock file; a deploy that cannot be recreated
  cannot be rolled back cleanly.

## Health Checks

- Health checks reflect real dependencies (DB, queue, external clients), not just process liveness.
- Startup checks gate traffic until the service can serve; shutdown drains gracefully.
- Readiness differs from liveness; both map to operational meaning.
- A readiness check that returns healthy while the service is broken produces
  "healthy but failing" incidents; the check should fail fast on its core path.

## Config And Secrets

- Config is typed, validated, and environment-aware; invalid config fails fast at startup.
- Secrets are injected via the platform secret manager, never in source or logs.
- Separate config from code: secrets, host, and environment-specific values live in
  the platform, not in the repository.

## Observability

- Logs are structured with correlation IDs and business context; decisions and state
  transitions, not noisy internals.
- Metrics cover latency, throughput, errors, saturation, and business health.
- Traces cross service and queue boundaries.
- Alerts map to user impact and have runbooks.

## SLOs And Capacity

- Define the SLO for the user-facing paths before the incident, not after.
- Set an error budget and a burn-rate alert, so pager noise matches user impact.
- Capacity planning answers "what happens at 2x traffic?" with numbers (pool sizes,
  queue depth, DB load), not adjectives.

## Runbooks

- One runbook per user-impacting failure mode: symptom, detection, diagnosis,
  mitigation, rollback, owner.
- Runbooks are discoverable from the alert that triggers them.

## Workers And Schedulers

- Idempotent and retry-safe with bounded retries and dead-letter handling.
- Backpressure and concurrency limits protect downstream systems.
- Backlog is visible in metrics and alerted.
- Scheduled jobs are idempotent and can resume: a missed tick should not corrupt state.

## Incident Response

- Timeline, user impact, technical contributors, detection gaps, recovery gaps,
  remediation, and follow-up ownership.
- Separate root-cause analysis from symptom patching.
- Define rollback first: the fastest safe recovery is the first line, analysis second.

## Zero-Downtime

- Compatibility deploy order; feature flags for risky behavior; observability before cutover.
- If zero-downtime is required, define it explicitly and test the deploy order.
- Signal the flag surfaces (feature flags, schema generation) as code, not lore.

## Change And Rollback Checklist

- Which deploy order does this change require (schema, code, worker)?
- What does a rollback look like for each artifact (revert + data compatibility)?
- What must be observed before and after cutover to call it a success?
- What happens if the new behavior must be disabled in seconds?
- Who owns the runbook for this change's failure mode?