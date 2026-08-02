# End-To-End Walkthrough: Add Billing Safely

Illustrative run of the full skill pipeline for a representative request. Every artifact
follows its skill's template. This is a fictional FastAPI service; it does not describe a
real repository.

## 1. Orchestrator: routing

Request: "Add recurring billing with webhooks and background reconciliation without
coupling the domain to Stripe."

Route: `python-senior-architect` -> `python-coder` -> `python-testing` ->
`python-security` -> `python-production` -> `python-reviewer`.

Handoff to architect:

```markdown
# Handoff
## Target Skill: python-senior-architect
## Objective: Plan recurring billing with webhook + reconciliation, domain decoupled from Stripe.
## Scope: subscription state machine, billing port, Stripe adapter, webhook boundary, outbox.
## Out Of Scope: UI, payments already refunded, third-party tax engines.
## Context: FastAPI + SQLAlchemy 2 + Celery; no billing domain today.
## Constraints: no provider payloads in domain; idempotent webhooks; zero-downtime schema change.
## Files Or Modules: app/domain/, app/application/, app/infrastructure/, app/handlers/.
## Expected Output: Implementation Plan with phases, contracts, tests, migration, risks.
## Validation: plan references real files and commands.
## Risks: duplicate invoices on retry, mixed schema versions.
## Definition Of Done: plan executable by Coder without redesign.
```

## 2. Architect: implementation plan

Output uses `python-senior-architect/templates/implementation-plan.md`:

```markdown
# Implementation Plan
## Goal: Recurring billing with durable, idempotent delivery.
## Non-Goals: UI, dunning emails, tax.
## Current State: no billing domain; webhook handler calls provider inline.
## Target Design:
- domain: Subscription, BillingProvider port (Protocol), domain events.
- application: BillingService (idempotent), ReconcileService.
- infrastructure: StripeBillingProvider, outbox writer.
- handlers: thin webhook endpoint.
## Affected Modules: app/domain/billing/, app/application/billing/, app/infrastructure/stripe/, app/handlers/webhooks.py.
## Required Abstractions: BillingProvider port; Outbox; idempotency key.
## Phases:
1. Schema: add outbox + idempotency columns (backward-compatible).
2. Domain + port + Stripe adapter behind feature flag.
3. Webhook handler writes outbox; worker consumes.
4. Cutover; remove inline path; monitor DLQ.
## Testing Strategy: unit for state machine; contract for Stripe adapter; integration for outbox.
## Migration And Rollout: expand-and-contract; flag INVOICE_OUTBOX; rollback = flag off.
## Risks And Mitigations: duplicates -> idempotency; backlog -> concurrency limit; schema drift -> deploy order.
## Delegation Notes For Python Coder: implement phase 1 and 2 first; keep domain free of Stripe types.
```

## 3. Coder: implementation + change report

Coder executes phases, then reports using `python-coder/templates/change-report.md`:

```markdown
# Change Report
## What Changed: added BillingProvider port, Stripe adapter, outbox writer, idempotency guard.
## Why: decouple domain from provider and make webhook retries safe.
## Files Touched: app/domain/billing/*, app/application/billing/*, app/infrastructure/stripe/*, migrations/001_outbox.*.
## Tests Or Validation Run: pytest app/domain/billing -q (passed); contract test for Stripe adapter (recorded fixture).
## Residual Risk: Stripe API shape may change; outbox cleanup TTL not decided.
## Follow-Up For Other Skills:
- Testing: integration coverage for outbox + worker.
- Security: verify webhook signature verification.
- Production: migration rollout order and DLQ monitoring.
```

## 4. Testing: test plan

`python-testing/templates/test-plan.md`:

```markdown
# Test Plan
## Behavior Under Test: webhook retry produces exactly one durable invoice; state transitions are legal.
## Target Layer: unit (state machine), integration (outbox + worker), contract (Stripe adapter).
## Failure Modes Covered: duplicate webhook, out-of-order events, provider timeout, DLQ.
## Tests To Add Or Update: retry-idempotency; invalid transition rejection; adapter schema drift.
## Fixtures And Factories Needed: Stripe webhook payload factory; outbox repository fake.
## Commands: pytest app/application/billing -q
## Validation And Acceptance: all new tests pass; old suite green.
```

## 5. Security: focused review

Checks webhook trust boundary: signature verification, no provider secrets in logs, tenant
isolation, timeouts on outbound Stripe calls. Approves with one required deny-path test.

## 6. Production: readiness

Confirms deploy order (schema -> worker -> webhook cutover), rollback via feature flag,
DLQ monitoring, correlation IDs across webhook -> outbox -> worker.

## 7. Reviewer: final PR review

`python-senior-architect/templates/pr-review.md` (architecture lens) plus
`python-reviewer/templates/review-report.md`:

```markdown
# Verdict: Approved with minor follow-ups.
## Blocking Findings: none.
## Non-Blocking Findings:
- [Medium] `app/infrastructure/stripe/adapter.py:31` - retry loop lacks exponential backoff; suggest jitter.
- [Low] outbox TTL cleanup undefined; add retention owner.
## Boundary Impact: none; domain remains provider-free.
## Migration Safety: expand-and-contract order correct; flag rollback verified.
## Test Coverage: idempotency and transition tests present; add one deny-path for unauthorized webhook.
## Follow-Up Work: backoff jitter; outbox retention; webhook deny-path test.
```

## Result

The feature lands with clear ownership at each stage, an executable contract between
skills, and documented validation at every handoff.
