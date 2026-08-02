# Example: FastAPI Hexagonal Service Review

Illustrative output of an architecture review for a FastAPI service. Represents the
shape of evidence-based analysis, not a real repository report.

## Executive Summary

The service follows a ports-and-adapters shape in the `billing` domain but leaks
infrastructure into application services in the `notifications` domain. Recommendation:
align `notifications` with the existing port/port-adapter convention and remove ORM
sessions from application logic.

## Evidence Reviewed

- `pyproject.toml`: FastAPI, SQLAlchemy 2, Pydantic v2, httpx, celery.
- Layout: `app/handlers/`, `app/application/`, `app/domain/`, `app/infrastructure/`, `tests/`.
- Imports: `app/application/notifications.py` imports `sqlalchemy.orm.Session` directly.
- Tests: unit tests cover `billing` domain; `notifications` has only route-level tests.

## Current Architecture

- `billing` domain: domain models framework-free; SQLAlchemy repository implements a `Protocol` port.
- `notifications` domain: application service owns a `Session`, builds rows inline.

## Findings

- [High] `app/application/notifications.py:14` — ORM session leaks into application layer; breaks domain isolation and testability.
- [Medium] `app/domain/notifications` imports `pydantic` schemas for persistence rows; schema and domain model conflated.
- [Low] `app/infrastructure` has two HTTP clients with overlapping retry logic.

## Recommendations

1. Introduce a `NotificationsRepository` port and SQLAlchemy adapter, mirroring `billing`.
2. Move persistence-row mapping out of `domain/notifications` into the adapter.
3. Consolidate HTTP client retry logic into one shared adapter.

## Risks

- Low blast radius; `notifications` is a leaf domain. No migration or API contract impact.
- Tests for `notifications` need rework to use fakes instead of a database.

## Open Questions

- Should repository adapter interfaces live in a shared `app/application/ports/` package?
