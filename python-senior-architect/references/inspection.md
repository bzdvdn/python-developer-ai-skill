# Project Inspection Strategy

Ground every architecture claim in repository evidence. Inspect in this order and record
assumptions, evidence, and confidence. Separate facts (what files, imports, and tests show)
from inferences (what they imply), and state confidence so the plan reader can weigh it.

## Repository Root

1. Read `README*`, `pyproject.toml`, `setup.cfg`, `setup.py`, `requirements*.txt`, `poetry.lock`, `uv.lock`, `tox.ini`, `noxfile.py`, `.python-version`.
2. Inspect directory layout with `rg --files` and summarize top-level packages, apps, tests, docs, scripts, migrations, and deployment files.
3. Check `AGENTS.md`, contribution docs, ADRs, `docs/`, and architecture notes.

## Frameworks And Entry Points

4. Identify frameworks from dependencies and imports: FastAPI, Django, Flask, Celery, SQLAlchemy, Pydantic, asyncio, aiohttp, httpx, Kafka, RabbitMQ, Redis, Airflow, Prefect, Typer, Click.
5. Identify entry points: web apps, ASGI/WSGI, CLIs, workers, scheduled jobs, notebooks, lambdas, scripts.
6. Inspect package roots and `__init__.py` boundaries.
7. Inspect dependency direction using imports from handlers, services, domain modules, repositories, adapters, tests, and configuration.

## Boundaries

8. Locate persistence: ORM models, migrations, repositories, SQL, sessions, transaction management.
9. Locate external integrations: HTTP clients, SDKs, queues, caches, object storage, auth providers, observability SDKs.
10. Locate testing strategy: unit, integration, contract, e2e, fixtures, factories, test database patterns.

## Inference

11. Infer conventions: naming, module layering, dependency injection style, settings model, error handling, logging, typing strictness.
12. Detect architecture style from evidence rather than labels.
13. Compare intended docs against actual imports and package layout.
14. Inspect changed files for reviews before inspecting unrelated code.
15. Record assumptions, evidence, and confidence.

## Anti-Patterns To Flag

- Cyclic imports and hidden shared state.
- Domain modules importing web frameworks, ORM sessions, queue envelopes, or HTTP clients.
- Handlers or CLI commands owning business workflows.
- ORM sessions, request objects, or queue envelopes leaking into application services or domain logic.
- Import-time side effects in `__init__.py` or settings modules.
- Framework objects embedded in domain models.
- Repository or service classes that are pure pass-throughs without design intent.

## Worked Example: Inspecting a FastAPI service

Request: "Does this FastAPI service follow clean architecture?"

Fixture evidence (the only ground truth):

```
app/handlers/orders.py         -> @router.post creates OrderService; imports order schema
app/application/orders.py      -> OrderService calls OrderRepository (Protocol)
app/domain/orders.py           -> Order aggregate; imports only stdlib + dataclasses
app/infrastructure/orders.py   -> SqlAlchemyOrderRepository (imports sqlalchemy)
app/models.py                  -> ORM rows (OrderModel, OrderItemModel)
tests/test_orders.py           -> unit tests on domain; one route test
pyproject.toml                 -> fastapi, sqlalchemy, pydantic
```

**Step 1 — metadata and layout.** `pyproject.toml` lists fastapi/sqlalchemy/pydantic.
`rg --files` shows `handlers/`, `application/`, `domain/`, `infrastructure/`, plus a
top-level `models.py`. Fact: the project is FastAPI + SQLAlchemy with a four-package layout.

**Step 2 — dependency direction.** For each package, list imports:
- `app/domain/orders.py` imports stdlib + dataclasses only. Fact: domain is framework-free.
- `app/infrastructure/orders.py` imports sqlalchemy. Fact: persistence lives at the edge.
- `app/application/orders.py` imports a `Protocol` for `OrderRepository`; does not import sqlalchemy.
- `app/models.py` is ORM rows and is imported by handlers and services.

**Step 3 — boundary leakage.** `app/models.py` is imported by `app/application/orders.py`
and by handlers. Fact: the same ORM classes are shared as domain objects. Inferences:
(i) domain concepts are expressed in ORM types, so persistence vocabulary leaks inward;
(ii) the route test likely constructs `OrderModel` directly, so unit tests may couple to the ORM.

**Step 4 — verify with tests and call sites.** `tests/test_orders.py` shows one route test
plus domain unit tests. Check whether the route test builds `OrderModel` in fixtures. Fact:
if it does, the ORM rows are load-bearing in test setup.

**Step 5 — separate facts from inferences for the verdict.**
- Fact: `domain` imports no frameworks; `infrastructure` owns SQLAlchemy; `application` depends on a Protocol. These match layered/clean intent.
- Fact: `app/models.py` ORM rows are shared as domain objects across handlers and application.
- Inference (medium confidence): the shared ORM rows are the main boundary leak, because domain invariants can be expressed in persistence types.
- Inference (low confidence, needs test evidence): tests may be route-coupled rather than behavior-coupled.

**Step 6 — produce the report.** Verdict: the service largely follows clean intent, with one
concrete boundary issue (`app/models.py` ORM rows shared as domain objects), and state the
confidence and the missing evidence rather than asserting the leak is "bad".

## Recording Evidence

For every claim you will put in a report, record:
- **Evidence:** file, line, import, or test that supports it.
- **Confidence:** high (direct evidence), medium (inferred from adjacent evidence), low (guess).
- **Missing evidence:** what you could not verify (deployment config, external docs, runtime behavior).
