# Async Testing Reference

Deterministic tests for async code. Prefer existing async plugins and conventions.

## Tooling

- Use `pytest-asyncio` when already configured, with explicit `asyncio_mode`.
- For frameworks, use their native async test client (FastAPI `httpx.AsyncClient`,
  Django async tests) instead of mixing test clients manually.
- Prefer `anyio` fixture variants when the repo supports both `asyncio` and `trio`.

## Determinism Rules

- Never `time.sleep`; use `await asyncio.sleep(0)` only for cooperative yield and
  `asyncio.Event`/`asyncio.Queue` for synchronization.
- Replace real timers and retry backoff with injected fakes that step deterministically.
- Replace real queue/clock/network with fakes implementing the same interface.

## Async Fakes

```python
class FakeQueue:
    def __init__(self, items: list[object] | None = None) -> None:
        self._items = list(items or [])

    async def get(self) -> object:
        if not self._items:
            raise StopAsyncIteration
        return self._items.pop(0)

    async def put(self, item: object) -> None:
        self._items.append(item)
```

## Common Failures

- **Unawaited tasks:** await or explicitly gather; use `pytest` warnings to detect leaks.
- **Event-loop leakage:** create loop-bound resources per test; avoid module-level
  event loops.
- **Blocking calls:** assert the code under test never calls sync I/O (linters and
  code review catch these; tests may use a blocking-detection helper).
- **Race flakiness:** prefer deterministic fakes over retrying the test.

## Retry And Backoff Tests

- Test success on first attempt.
- Test transient failure then success (fake raises once).
- Test permanent failure reaches the dead-letter/abandon path.
- Assert backoff is bounded and configurable, without sleeping.
