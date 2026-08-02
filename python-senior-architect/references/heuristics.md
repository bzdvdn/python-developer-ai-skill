# Architectural Heuristics

Use these as defaults, not dogma. Repository evidence and local conventions override them.

## Dependency Direction And Boundaries

1. Avoid cyclic dependencies between packages.
2. Respect dependency direction from outer layers to inner policy.
3. Keep domain logic independent from frameworks.
4. Keep infrastructure details out of domain models.
5. Keep HTTP handlers thin.
6. Keep CLI commands thin.
7. Keep message consumers thin.
8. Put business workflows in application services or use cases.
9. Prefer composition over inheritance.
10. Introduce abstractions after concrete pressure exists.
11. Do not create interfaces with only speculative value.
12. Use ports for external systems with meaningful volatility.
13. Use adapters to isolate framework and infrastructure details.
14. Keep persistence models separate from domain models when behavior or lifecycle differs.
15. Avoid anemic domain models only when behavior naturally belongs with data.
16. Avoid over-rich domain objects that need databases, HTTP clients, or clocks directly.
17. Pass clocks, ID generators, and external clients as dependencies.
18. Treat time, randomness, and network calls as boundary concerns.
19. Prefer explicit dependency injection over hidden globals.
20. Avoid service locators unless the framework forces them.

## Package And Context Design

21. Keep package names aligned with business capabilities where possible.
22. Avoid organizing everything only by technical layer in large domains.
23. Use bounded contexts when terms or invariants diverge.
24. Do not share mutable domain objects across bounded contexts.
25. Prefer published contracts between contexts.
26. Keep DTOs at boundaries.
27. Do not leak ORM sessions into domain logic.
28. Do not leak web request objects into application services.
29. Do not leak queue message envelopes into domain logic.
30. Keep transactions explicit and scoped.
31. Avoid long transactions across network boundaries.

## Messaging And Consistency

32. Use idempotency for external side effects.
33. Make message handlers idempotent.
34. Prefer at-least-once messaging assumptions unless exactly-once is proven.
35. Use outbox or transaction log patterns when publishing events from database changes.
36. Do not publish integration events before durable state is committed.
37. Distinguish domain events from integration events.
38. Avoid synchronous distributed call chains for critical user paths.
39. Use async only when concurrency or latency profile justifies it.
40. Do not mix blocking I/O into event loops.
41. Keep async boundaries explicit.
42. Use backpressure for consumers and producers.

## Caching And Persistence

43. Cache only with clear invalidation semantics.
44. Prefer correctness before cache complexity.
45. Keep cache keys versioned and observable.
46. Avoid using cache as the source of truth.
47. Design persistence around aggregates and queries, not table convenience alone.
48. Use CQRS when read and write models have materially different needs.
49. Avoid CQRS for simple CRUD unless complexity is already justified.

## API And Migration

50. Keep APIs stable and versioned when clients are external.
51. Prefer backward-compatible schema changes.
52. Use expand-and-contract migrations for zero downtime.
53. Make rollout reversible where possible.
54. Use feature flags for risky behavior changes.
55. Prefer branch by abstraction for long migrations.

## Observability

56. Keep observability near boundaries and workflows.
57. Log decisions and state transitions, not noisy internals.
58. Trace cross-service workflows with correlation IDs.
59. Define metrics for latency, throughput, error rate, saturation, and business invariants.

## Testing

60. Ensure tests cover architecture-critical contracts.
61. Use contract tests for adapters and external integrations.
62. Use integration tests for transactions and persistence boundaries.
63. Use unit tests for pure domain logic.
64. Avoid brittle tests coupled to implementation details.

## Design General

65. Keep public APIs small and intentional.
66. Prefer explicit errors over sentinel values.
67. Model failure modes as first-class design concerns.
68. Keep configuration typed, validated, and environment-aware.
69. Avoid import-time side effects.
70. Keep startup wiring separate from business logic.
71. Prefer boring technology for core paths.
72. Optimize for removability of decisions.
73. Preserve existing conventions unless there is a clear payoff.
74. Do not recommend a rewrite when a strangler migration can work.
75. Treat architecture as socio-technical: ownership and operability matter.
