# Evals: python-security

## Scenario: security-authz-bypass

### Prompt
Review this endpoint that lets users update invoices.

### Repository Fixture
```
app/handlers/invoices.py  -> PUT /invoices/{id} loads invoice by id, no ownership check
app/services/auth.py      -> get_current_user() exists
tests/test_invoices.py    -> happy path only
```

### Expected Behavior
- Traces authentication, resource lookup, ownership, and permission checks.
- Flags missing object-ID ownership check as a confirmed exploit path.
- Requires a deny-path test.

### Acceptance Criteria
- [ ] Identifies missing ownership check with a concrete path.
- [ ] Explains exploitability and impact, not just "add validation".
- [ ] Recommends deny-path test for unauthorized user.

### Anti-Criteria
- [ ] Checks authentication only and misses resource ownership.
- [ ] Treats generic hardening advice as a finding.

## Scenario: security-ssrf

### Prompt
Add user-provided callback URLs for webhooks.

### Repository Fixture
```
app/services/callbacks.py -> fetches url from user input with httpx
app/config.py              -> no allowlist
```

### Expected Behavior
- Inspects URL parsing, allowlists, redirects, DNS/private-IP handling, timeouts.
- Flags missing timeout and missing private-network guard as concrete issues.
- Separates confirmed vulnerabilities from missing evidence.

### Acceptance Criteria
- [ ] Flags SSRF risk (user-controlled URL, no allowlist, no timeout).
- [ ] Suggests allowlist/timeout fix with a deny-path test.

### Anti-Criteria
- [ ] Recommends custom crypto or ad hoc parsing.
- [ ] Assumes deployment protections exist without evidence.

## Scenario: security-secrets

### Prompt
Review OAuth token storage.

### Repository Fixture
```
app/auth/tokens.py -> stores token in domain object, serialized into events and logs
```

### Expected Behavior
- Inspects persistence, encryption/secret-manager usage, logs, exceptions, fixtures.
- Flags tokens leaking into serialized events and logs.

### Acceptance Criteria
- [ ] Flags token in domain object/event/log with path.
- [ ] Recommends standard secret handling (not custom crypto).

### Anti-Criteria
- [ ] Recommends inventing a new crypto scheme.
- [ ] Logs sensitive values while "fixing" errors.
