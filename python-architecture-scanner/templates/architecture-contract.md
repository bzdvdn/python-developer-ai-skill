# Architecture Contract

Define layers and rules so they can be checked deterministically. This file maps
first-party package roots to layers and lists forbidden import rules.

## Layer Map

| Layer | Package roots |
| --- | --- |
| `domain` | `app/domain` |
| `application` | `app/application` |
| `infrastructure` | `app/infrastructure` |
| `handlers` | `app/handlers` |

## Forbidden Rules

- `domain` must not import: `infrastructure`, `handlers`, and third-party keywords
  (`web`, `orm`, `queue`, `cache`, `http_client`, `storage`).
- `application` must not import: `handlers`.

## Machine-Readable Form

```json
{
  "layers": {
    "domain": ["app/domain"],
    "application": ["app/application"],
    "infrastructure": ["app/infrastructure"],
    "handlers": ["app/handlers"]
  },
  "forbidden": [
    {"from": "domain", "to": ["infrastructure", "handlers", "web", "orm", "queue", "cache", "http_client", "storage"]},
    {"from": "application", "to": ["handlers"]}
  ]
}
```

Run with `scripts/check_layer_rules.py`; it exits non-zero on violations so it can gate CI.

## Review Checklist

- [ ] Layers match the repo's actual package roots.
- [ ] Every rule reflects an intended boundary, not a passing whim.
- [ ] Test-only and type-only imports are handled explicitly.
- [ ] Rule changes are reviewed like code.
