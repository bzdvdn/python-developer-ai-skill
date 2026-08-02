# Example: Django Layering Review

Illustrative output of a layering review for a Django project. Represents the shape
of evidence-based analysis, not a real repository report.

## Executive Summary

Django's `apps/` layout is sound, but business logic has drifted into views and
`models.py` methods now depend on framework signals. Recommend moving workflow
logic into service functions and keeping models as persistence + thin domain state.

## Evidence Reviewed

- `settings.py`, `urls.py`, installed apps, `apps/` package layout.
- `apps/orders/views.py`, `apps/orders/services.py`, `apps/orders/models.py`.
- Tests: `apps/orders/tests/` covers views and one service.

## Findings

- [High] `apps/orders/views.py:41` — checkout workflow (payment call, stock decrement, email)
  orchestrated in the view; not reusable and hard to test.
- [Medium] `apps/orders/models.py:88` — `Order.cancel()` fires a `post_save` signal that reaches
  into an external service; signals make state transitions implicit and hard to trace.
- [Low] `apps/orders/services.py` exists but only two functions; most workflows still live in views.

## Recommendations

1. Move checkout into `apps/orders/services.py` as a pure service function with explicit dependencies.
2. Replace `post_save` signal side effects with an explicit service call or a domain event published after commit.
3. Add unit tests for service functions with fakes for payment and email providers.

## Risks

- Medium: view behavior changes touch response shapes; keep responses identical during the move.
- Signals may be wired in other apps; audit `post_save` receivers before removal.

## Open Questions

- Is `django-tenant-schemas` isolation enforced at the queryset layer or only middleware?
