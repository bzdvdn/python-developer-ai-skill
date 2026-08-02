# Architecture Patterns Primer

A condensed reference for identifying and recommending architecture patterns from repository
evidence. Use only when the evidence justifies them; never prescribe a pattern because the
name sounds senior. Every recommendation must name the concrete problem the pattern solves
better than the current shape.

## Layered Architecture

- **Shape:** handlers/CLI/workers -> services -> repositories, each layer depends only inward.
- **Evidence:** `handlers/`, `services/`, `repositories/`, `models/` packages; thin handlers calling services.
- **When:** CRUD-heavy apps, familiar team, framework-driven web services.
- **Watch for:** anemic services, repository pass-throughs, ORM models reused as domain models.

## Clean / Onion Architecture

- **Shape:** domain core with no dependencies, application services, infrastructure adapters at edges.
- **Evidence:** `domain/`, `application/`, `infrastructure/` packages; domain imports only stdlib + local contracts.
- **When:** complex business rules, high test value in domain, expected long lifespan.
- **Watch for:** speculative ports, over-abstracted infrastructure, ceremony outpacing real coupling.

## Hexagonal / Ports And Adapters

- **Shape:** application core exposes ports (interfaces); adapters implement them for web, DB, queues, HTTP.
- **Evidence:** `Protocol`/ABC ports in application layer, adapters in infra, domain has no external imports.
- **When:** volatile external systems, several adapters per port, strong test isolation.
- **Watch for:** ports with a single implementation, adapter logic leaking into application services.

## DDD And Bounded Contexts

- **Shape:** modules map to business capabilities; contexts share published contracts, not mutable objects.
- **Evidence:** package names by capability (`billing/`, `inventory/`, `ordering/`), aggregates, domain events.
- **When:** large domain, divergent terms or invariants, multi-team codebase.
- **Watch for:** shared mutable domain objects, context boundary erosion, events only as ceremony.

## Event-Driven And CQRS

- **Shape:** producers publish events; consumers react; read and write models may diverge.
- **Evidence:** message producers/consumers, outbox, event schemas, separate read projections.
- **When:** decoupling, scale, async workflows justify it.
- **Watch for:** synchronous request/response duct-taped onto events, missing idempotency, events used for RPC.

## Monolith vs Modular Monolith vs Microservices

- **Shape:** one deployable with clear internal boundaries vs independently deployed services.
- **Evidence:** deployment units, package boundaries, shared databases, cross-service calls.
- **Recommendation default:** modular monolith unless team size, ownership, or scaling forces services.
- **Watch for:** distributed monolith (network-coupled modules sharing one database).

## Choosing

- Match the pattern to the demonstrated volatility, domain complexity, and team familiarity.
- Prefer the smallest pattern that makes the real coupling explicit.
- Any new pattern must have at least one concrete problem it solves better than the current shape.

## Worked Example: Identifying the pattern from evidence

Request: "Which pattern does this service follow, and should we add one?"

Fixture evidence:

```
app/handlers/orders.py        -> thin route, calls OrderService, maps request/response
app/application/orders.py     -> OrderService, depends on OrderRepository Protocol, raises domain errors
app/domain/orders.py          -> Order aggregate, dataclasses only, no imports outside stdlib
app/infrastructure/orders.py  -> SqlAlchemyOrderRepository implements the Protocol
app/models.py                 -> ORM rows
tests/test_orders.py          -> domain unit tests; one route test using a fake repository
```

**Reasoning.**
1. The `domain/` package imports only stdlib -> evidence of a dependency-inverted core, which
   matches Clean/Onion or Hexagonal shape.
2. The application layer depends on a `Protocol` (`OrderRepository`) and the infrastructure
   package implements it -> evidence of ports-and-adapters.
3. There is a single implementation of the repository port today. That is a signal the pattern
   may be over-applied unless the second implementation (in-memory fake, another DB, or an HTTP
   store) already exists in tests — check `tests/` for a fake. If only one implementation exists
   and no second is planned, the port is speculative: name that trade-off rather than endorsing it.
4. `app/models.py` ORM rows shared as domain objects is a boundary leak in both Clean and
   Hexagonal readings: domain concepts are expressed in persistence types.

**Verdict pattern.** "Layered intent with a dependency-inverted core (Clean/Hexagonal shape):
domain is framework-free, application depends on a Protocol. The shared ORM rows are the
boundary leak. The repository port currently has one implementation — keep it only if a second
implementation is justified, otherwise drop it." This recommends the shape without prescribing
more pattern than the evidence supports.

## Worked Example: Rejecting a pattern the repo does not need

Request: "Should we adopt CQRS for the order list?"

Fixture evidence: `GET /orders` and `POST /orders` both read and write the same `Order` rows;
there is no material read/write divergence; the slow query is a missing index, not a model problem.

**Reasoning.** CQRS is only justified when read and write models materially diverge — separate
read projections, different consistency needs, or high read scaling. Here the read and write
shapes are the same table, and the actual problem is a query plan. Adopting CQRS adds a
projection store, invalidation, and read-model synchronization for a problem that an index solves.

**Verdict pattern.** "Keep the current shape; add an index and a query-count regression test.
Do not introduce CQRS: read and write models do not diverge." Rejection is grounded in the same
evidence rule as adoption: a pattern must solve a demonstrated problem.
