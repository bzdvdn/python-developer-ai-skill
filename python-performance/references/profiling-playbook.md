# Profiling Playbook

Evidence-first workflow for Python performance work. Measure before changing;
never present a suspected bottleneck as a measured one.

## Define The Symptom

- Reproduce the symptom: endpoint, job, workload, concurrency, target.
- Capture a baseline number (latency, throughput, memory) before touching code.
- State the percentile you care about: a mean hides a bad tail. Record p50, p95, p99.
- Record the run duration and workload so a later run is comparable.

## Measurement Methodology

- Measure the thing the user asked about, not the thing that is convenient to time.
- Warm up before timing; drop the first N requests when there is lazy initialization.
- Iterate enough repetitions that noise beats the effect size.
- Keep the environment stable across runs (load, data size, CPU isolation) so the
  before/after comparison is valid.
- A single sample is a rumour; a distribution is evidence.

## Localize, Don't Guess

Work from the cheapest evidence to the most invasive:

1. Code-path review: query counts, loop nesting, repeated I/O.
2. Database evidence: query logs, `EXPLAIN ANALYZE`, N+1 counts.
3. CPU profiling: `cProfile`, `py-spy` for a running process, `scalene`.
4. Memory: `tracemalloc`, heap snapshots, RSS over time.
5. Load: `locust`/`wrk` for throughput and latency under concurrency.

## Choosing A Profiler

| Situation | Tool | Notes |
| --- | --- | --- |
| Whole call graph of an entrypoint | `cProfile` | call counts + cumulative/self time; sort with `-s tottime` |
| A running production process | `py-spy` | no code change; `py-spy dump` shows a snapshot, `record` a flamegraph |
| Line-level CPU and memory | `scalene` | per-line attribution without deep sampling annotations |
| Where memory is allocated | `tracemalloc` | snapshots and top allocations by site |
| Process/OS-level pressure | `ps`, RSS over time, `perf stat` | complements Python profilers |

- Profile the *representative* code path; a microbenchmark of a hot function is a start,
  not the finish.
- Confirm the profile matches the symptom. If the profile points somewhere unrelated,
  the symptom definition was wrong.

## Database And Query Evidence

- Collect the actual queries with a logger or driver flag: count per request, their
  SQL, and per-query time.
- For a slow query run `EXPLAIN (ANALYZE, BUFFERS)` and look for seq scans, missing
  indexes, and rows-after-filter gaps.
- Count N+1: the same query shape issued once per parent row. Batch into a single `IN`.
- Check connection usage: pool size, connection churn, lack of reuse, and commits
  inside a per-item loop.
- Set timeouts on database clients and external calls; tail latency often comes from an
  unbound retry.

## Async And Concurrency Evidence

- Look for blocking calls inside `async def` bodies and on the event loop:
  `requests`, blocking DB APIs, `time.sleep`, CPU-heavy work without `run_in_executor`.
- Inspect a live process with `py-spy dump` (or `py-spy record`) to see what a worker
  is blocked on when the backlog grows.
- Check maintained concurrency: unbounded task creation vs a `Semaphore`/worker bound.
- Distinguish *many* tiny tasks (event-loop overhead) from *few* slow tasks (blocking I/O).
- A core-saturating loop or heavy CPU in async code is still CPU-bound; scheduling it
  into a thread/process pool does not always help and can add copying costs.
- Ask levantar whether the bottleneck is concurrency turnover, throughput, or latency —
  they have different fixes.

## Common Bottlenecks

- N+1 queries; expensive work repeated inside loops.
- Blocking libraries in async code (`requests`, sync DB sessions on the event loop).
- Unbounded result sets and pagination gaps.
- Serialization cost on hot paths (Pydantic, JSON, repeated validation).
- Pool exhaustion (DB, HTTP) under concurrency.
- Unbounded retry loops and retained payloads driving memory growth.
- Missing timeouts and retries amplifying idle latency.
- Repeated filesystem access that could be cached or batched.

## Caching Advice, Only After Evidence

- Add a cache only after the profile shows repeated expensive work with a storable
  result. A cache hunting for a problem is a complexity tax.
- Define before writing: key format and version, TTL/invalidation, write-through or
  cache-aside, and whether staleness is acceptable.
- Protect against stampede on cold cache (single-flight), and keep the cache keyed by
  the runtime-affecting inputs so it is not the source of truth.
- Add metrics for hit ratio, TTL age, and stampede before deploying.

## Result And Trade-off Checklist

- Re-measure against a fixed baseline with the same workload.
- Report before/after numbers and remaining unknowns.
- State operational trade-offs: memory, consistency, cache staleness, complexity.
- A change that improves p50 but worsens p99 is a trade-off, not a success.

## Anti-Patterns

- "It's slow" with no baseline. When a symptom is not measurable the fix is not provable.
- Optimizing code the profile never shows as a hotspot.
- Silently changing semantics, ordering, pagination, or consistency for speed.
- Claiming a fix without the before/after numbers.
- Adding a cache or parallelism where the cost is concurrency overhead rather than work.