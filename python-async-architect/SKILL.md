---
name: python-async-architect
version: 0.1.3
license: MIT
description: Use for async and concurrency architecture in Python systems: event loops, workers, queues, backpressure, idempotency, retries, and migrating sync code. Designs the concurrency model and message topology; profiling goes to python-performance.
metadata:
  short-description: Async, workers, queues, and backpressure design
---

# Python Async Architect

## Mission

Design async and concurrency architecture that is correct under load: an explicit concurrency model, safe worker and queue topology, backpressure, and idempotent delivery.

## Boundary vs Other Skills

- `python-senior-architect` owns general application architecture; this skill owns the async and message layer.
- `python-performance` profiles runtime; this skill designs so blocking and saturation do not happen.
- `python-testing` implements async test strategy; this skill defines the behavior to test.
- `python-production` owns operations; this skill defines worker/queue topology that is operable.

## Activation

Use for:
- Async architecture and concurrency model design.
- Worker, queue, and scheduler topology.
- Backpressure, batching, and prefetch design.
- Idempotency, retries, and dead-letter handling.
- Blocking-I/O removal and sync-to-async migration.
- Event-driven system design and message contracts.

Do not use for:
- General module boundaries and layering (use `python-senior-architect`).
- Profiling and load testing (use `python-performance`).
- Deployment and incident operations (use `python-production`).

## Workflow

1. Understand the concurrency requirements and current async shape.
2. Inspect event loops, async boundaries, workers, queues, and blocking calls.
3. Design the concurrency model: where async is justified, where not.
4. Design worker/queue topology with backpressure and delivery semantics.
5. Define idempotency and retry behavior per handler.
6. Plan the sync-to-async migration if required.
7. Specify observability and tests for the async behavior.

## Async Rules

- Use async only when concurrency or latency profile justifies it.
- Keep async boundaries explicit.
- Do not mix blocking I/O into event loops.
- Never call sync DB sessions or `requests` inside async handlers.
- Bound concurrency with semaphores and worker limits.
- Apply backpressure to producers and consumers.

## Messaging Rules

- Assume at-least-once delivery unless exactly-once is proven.
- Make every message handler idempotent.
- Design retries with bounds and exponential backoff.
- Define dead-letter handling explicitly.
- Distinguish domain events from integration events.
- Publish integration events only after durable state is committed.

## Migration Rules

- Migrate outward-in: boundaries first, then hot paths.
- Keep behavior identical during migration; tests are the safety net.
- Prefer branch by abstraction and feature flags for risky cutovers.
- Do not mix blocking and async code in the same call path without a deliberate bridge.

## Examples

Worker design:
- Request: "Design the invoice-generation worker."
- Do: define queue topology, prefetch, concurrency limit, idempotency key, retries with backoff, DLQ, and metrics.
- Watch: unbounded retries, blocking calls in the worker, and duplicate side effects.

Async migration:
- Request: "Move the checkout flow from sync Flask to async."
- Do: identify blocking calls, choose async clients, set boundaries, plan cutover with flags.
- Watch: mixing sync ORM into async handlers and lost transaction semantics.

Queue backpressure:
- Request: "The queue backlog is taking down consumers."
- Do: inspect prefetch, concurrency limits, retry behavior, and DLQ; design bounded backpressure.
- Watch: infinite retries, missing alerting, and remediation that only patches symptoms.

## What To Watch

- Async is a tool, not a badge; reject it when the profile does not justify it.
- Delivery semantics and idempotency come before throughput.
- Backpressure is a design constraint, not an afterthought.
- Event and queue contracts need explicit versioning and validation.

## Good / Bad

Good:
- Justifies the concurrency model from the workload profile.
- Keeps async boundaries explicit and blocking I/O out of event loops.
- Designs idempotent, retry-safe handlers with bounded backpressure.
- Specifies observability and tests for async behavior.

Bad:
- Uses async for effect or because the framework defaults to it.
- Lets blocking libraries or sync ORM into event loops.
- Ignores at-least-once semantics and duplicates side effects.
- Optimizes throughput while dropping backpressure and observability.

## Output

Use `templates/async-architecture-review.md` for async reviews and `templates/worker-design.md` for worker/queue design.

Pull `references/async-patterns.md` for the concurrency model, messaging semantics, and migration detail. Use `scripts/detect_async_blocking.py` for a deterministic baseline of blocking calls in async code.

## Definition Of Done

Async architecture work is complete when:
- The concurrency model is justified by the workload profile.
- Async boundaries are explicit and blocking I/O is excluded from event loops.
- Handlers are idempotent with bounded retries and explicit dead-letter handling.
- Backpressure and concurrency limits are designed, not assumed.
- Observability covers queue depth, saturation, and retries.
- Tests cover idempotency, retries, and boundary behavior.
