# Async Patterns

Depth material for async and messaging design. Use as guidance, not law.

## Concurrency Model

- Async pays off for I/O-bound, latency-sensitive paths; it is a tax otherwise.
- Keep async boundaries explicit: a caller knows whether a function is async.
- Never mix blocking I/O into event loops; use async clients and async DB drivers.
- Bound concurrency with semaphores and worker limits instead of unbounded tasks.

```python
async def fetch_many(client: httpx.AsyncClient, ids: list[str], limit: int = 10) -> list[Profile]:
    sem = asyncio.Semaphore(limit)
    async def one(uid: str) -> Profile:
        async with sem:
            response = await client.get(f"/profiles/{uid}", timeout=5.0)
            response.raise_for_status()
            return Profile.model_validate(response.json())
    return await asyncio.gather(*(one(uid) for uid in ids))
```

## Tasks And The Event Loop

- Every `TaskGroup`/`gather` stretches assumptions: a sibling that raises or hangs can
  stall the whole group, so scope tasks and handle per-task errors deliberately.
- CPU-bound work on the loop blocks every other task; offload with `run_in_executor`
  only when measurement shows CPU is the bottleneck.
- Cancel cleanly: wrap work that must finish in `finally`/`async with`, and use
  explicit cancellation points rather than swallowing errors.
- Timeouts are a contract, not an afterthought. Every external await should have a
  bound (`asyncio.timeout`, client timeouts) so a hung dependency cannot stop the worker.

## Timeouts, Retries And Cancellation

- Bound each external call with a timeout tied to the leading constraint (e.g. downstream
  SLO); do not let one slow peer hold the whole batch.
- Retries only for transient failures, with exponential backoff + jitter and a max count.
- Separate the "transient then success" path from "permanent failure" to dead-letter.
- Handle `CancelledError` correctly: only complete cleanup, then re-raise.

## Messaging Semantics

- Assume at-least-once unless exactly-once is proven end to end.
- Make handlers idempotent: deduplicate on a unique key.
- Retries are bounded with exponential backoff and jitter.
- Dead-letter queues are explicit and monitored.
- Start with at-least-once + idempotent handlers; exactly-once is a hard-fought property,
  not a setting.
- Distinguish domain events (meaningful to the domain) from integration events (for
  other systems or consumers).
- Publish integration events only after the state they describe is durable (outbox).

## Backpressure And Queues

- Producers should respect consumer capacity; consumers should signal saturation.
- Set prefetch and concurrency limits explicitly (message, worker reads you configure).
- A growing backlog is a design signal, not just an ops event.
- Ask which side is the constricted: producer rate, consumer speed, downstream API, or
  queue retention.
- When consuming, use ack/commit deliberately: ack after the business effect is durable,
  and design the redelivery path for a crash between effect and ack.

## Sync-To-Async Migration

- Migrate outward-in: adapter boundaries first, then hot paths.
- Replace sync clients with async equivalents before touching domain logic.
- Keep behavior identical; tests are the safety net.
- Use branch by abstraction and feature flags for risky cutovers.
- Do not interleave blocking and async in one path without a deliberate bridge
  (e.g., a dedicated executor) and an explicit ownership boundary.

## Idempotency And Retries

- Persist the idempotency key with the side effect, transactionally where possible.
- On retry, return the stored result instead of repeating the side effect.
- Design the "forgiving" and "permanent failure" paths separately.

## Testing Async And Messaging

- Drive time deterministically: control virtual time, inject failures, and assert on
  cancellation rather than real sleeps.
- Test idempotency by replaying the same message/key; assert a single side effect.
- Test backpressure by saturating a bounded worker and asserting ack ordering and no loss.
- Test the delivery guarantee the contract claims (at-least-once: redelivery produces
  no duplicates).

## Observability

- Trace across process and queue boundaries with correlation IDs.
- Metrics: queue depth, consumer lag, retry count, DLQ size, handler latency.
- Metric per-state (in-flight, prefetched-but-unacked, dead-lettered) so saturation and
  creep are distinguishable.
- Alerts map to user impact, not just saturation internals.