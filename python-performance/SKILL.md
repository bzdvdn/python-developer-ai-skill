---
name: python-performance
version: 0.1.4
license: MIT
description: Use to measure and improve Python performance: slow endpoints, memory, database queries, async bottlenecks, caching, queue throughput, latency, and scalability. Profiles before recommending changes; concurrency or queue design belongs to python-async-architect.
metadata:
  short-description: Analyze and improve Python performance
---

# Python Performance

## Mission

Improve Python performance with evidence. Measure first, localize bottlenecks, then propose or implement the smallest effective change.

## Activation

Use for:
- Slow endpoints, jobs, tests, or CLIs.
- High CPU, memory, latency, or database load.
- Async bottlenecks and blocking calls.
- Caching strategy.
- Queue throughput and worker scaling.
- Profiling and benchmark design.

## Workflow

1. Define the performance symptom and target.
2. Inspect relevant path and workload.
3. Look for obvious query, I/O, async, cache, and algorithm risks.
4. Profile or benchmark when feasible.
5. Separate measurement from hypothesis.
6. Recommend smallest safe fix.
7. Add regression benchmark or test when useful.

## Checklist

- Database queries avoid N+1 patterns.
- Expensive work is not repeated inside loops.
- External calls have timeouts and batching where appropriate.
- Async paths do not call blocking libraries.
- Memory growth is bounded.
- Cache has correct invalidation and key strategy.
- Queue workers have backpressure and concurrency limits.
- Pagination or streaming protects large result sets.
- Serialization cost is understood on hot paths.
- Metrics exist for latency, throughput, errors, and saturation.

## Tools

Use configured tests and benchmarks first. Use `pytest-benchmark`, `py-spy`, `scalene`, `cProfile`, database explain plans, app metrics, `locust`, or `wrk` when available and appropriate.

Pull `references/profiling-playbook.md` for the evidence-first profiling workflow, common bottlenecks, and fix rules.

## Examples

Slow endpoint:
- Request: "The order list endpoint is slow."
- Do: identify the endpoint path, query count, serialization cost, pagination behavior, and available metrics or tests.
- Watch: N+1 queries, unbounded result sets, expensive per-row work, and fixes that change response semantics.

Memory growth:
- Request: "Worker memory climbs during imports."
- Do: inspect loops, batching, retained collections, streaming behavior, and profiler or heap evidence when feasible.
- Watch: loading entire files into memory, global caches without bounds, and retry loops that retain failed payloads.

Async bottleneck:
- Request: "FastAPI gets slower under concurrent requests."
- Do: inspect async handlers for blocking libraries, connection pool limits, external calls, and timeouts.
- Watch: `requests` in async code, sync database sessions on the event loop, pool exhaustion, and missing backpressure.

## What To Watch

- Measure or gather evidence before recommending invasive changes.
- Separate symptoms, hypotheses, and confirmed bottlenecks.
- Optimize hot paths without reducing correctness or observability.
- Caches need invalidation, key design, and metrics.
- Performance work should include a way to notice regression later when practical.

## Good / Bad

Good:
- Defines the symptom, workload, and target before optimizing.
- Uses metrics, profiling, query counts, benchmarks, or code evidence.
- Fixes the confirmed bottleneck with the smallest behavior-preserving change.
- Mentions trade-offs such as memory, consistency, cache invalidation, or operational complexity.
- Adds benchmark or regression coverage when the hot path is important.

Bad:
- Guesses the bottleneck from code style alone.
- Adds caching before understanding freshness and invalidation.
- Optimizes cold paths while ignoring database or network costs.
- Changes semantics, ordering, pagination, or consistency for speed without saying so.
- Reports improvement without a baseline or validation method.

## Output

Report evidence, bottleneck, expected impact, fix options, trade-offs, validation, and remaining unknowns.
Use `templates/performance-report.md` when a structured performance report is useful.

## Definition Of Done

Performance work is complete when:
- The symptom, workload, and target are defined or the missing target is called out.
- Baseline evidence is gathered from metrics, profiling, benchmarks, query counts, or code-path evidence when feasible.
- Hypotheses are separated from confirmed bottlenecks.
- Fix options preserve correctness, API behavior, ordering, consistency, and observability unless trade-offs are explicit.
- Validation or regression measurement is recommended or run.
- Remaining unknowns and operational trade-offs are stated.
