# Example: Celery Migration Plan

Illustrative migration plan for moving a background job pipeline from inline async tasks
to a durable Celery worker with an outbox. Represents the shape of a bounded, reversible plan.

## Goal

Move invoice generation off the request path into a durable worker while guaranteeing
at-least-once delivery without duplicate invoices.

## Non-Goals

- No schema rewrite beyond adding an outbox table and idempotency key column.
- No change to the public invoice API contract.

## Current State

- Inline `await generate_invoice(...)` in the webhook handler.
- If the handler retries, invoices duplicate because no idempotency key is stored.

## Target Design

- Webhook handler writes an outbox row and commits.
- A Celery task reads outbox rows, processes them, and marks them delivered.
- Invoice creation is guarded by a unique idempotency key.

## Phases

1. Add `outbox` table and `idempotency_key` column; backfill empty.
2. Add a `generate_invoice` Celery task that is idempotent on the key.
3. In dual-run mode, keep the inline path and add the outbox writer behind a feature flag.
4. Cut over: webhook writes outbox; worker consumes; inline path removed.
5. Monitor dead-letter queue and stuck outbox rows; remove flag.

## Testing Strategy

- Unit: task retry with the same key produces one durable invoice.
- Integration: webhook commit + worker consume against a test database.
- Contract: invoice payload schema compatibility.

## Migration And Rollout

- Deploy order: schema first, task second, webhook cutover last.
- Feature flag `INVOICE_OUTBOX` controls the switch.
- Rollback: set flag off; inline path remains intact.

## Risks And Mitigations

- Duplicate delivery: mitigated by idempotency key.
- Worker backlog: backpressure via concurrency limit and DLQ monitoring.
- Mixed schema versions: outbox table added before any writer is deployed.

## Open Questions

- Who owns cleanup of old outbox rows and retention policy?
