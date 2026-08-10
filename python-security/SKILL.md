---
name: python-security
version: 0.1.3
license: MIT
description: Use for Python security review involving authentication, authorization, secrets, input validation, dependency vulnerabilities, SSRF, injection, deserialization, cryptography usage, tenant isolation, and secure deployment defaults.
metadata:
  short-description: Review Python security risks
---

# Python Security

## Mission

Identify and reduce security risk in Python systems. Focus on exploitable behavior, trust boundaries, unsafe defaults, and dependency risk.

## Activation

Use for:
- Auth and authorization changes.
- Secrets and credentials handling.
- Input validation and parsing.
- External HTTP calls and SSRF risk.
- SQL, command, template, or path injection.
- Unsafe deserialization.
- Dependency vulnerability review.
- Multi-tenant isolation.
- Security-sensitive PR review.

## Workflow

1. Identify trust boundaries.
2. Inspect changed code and adjacent authorization paths.
3. Inspect config, dependency, and deployment assumptions.
4. Run configured security tools when useful.
5. Prioritize exploitable risks over theoretical style concerns.
6. Recommend minimal safe fixes and tests.

## Checklist

- Authentication is enforced at the intended boundary.
- Authorization checks use resource ownership and tenant context.
- Secrets do not appear in source, logs, errors, metrics, or domain objects.
- Inputs are validated at boundaries.
- SQL and shell execution avoid string interpolation.
- Deserialization avoids unsafe loaders and arbitrary object construction.
- External requests use allowlists, safe URL handling, and timeouts.
- Passwords, tokens, and keys use standard libraries and secure algorithms.
- Dependencies are pinned and auditable where project policy requires it.
- Error messages do not leak sensitive internals.
- Security behavior has tests for allow and deny paths.

## Tools

Use configured `bandit`, `pip-audit`, `semgrep`, dependency lock inspection, and framework security checks. Prefer official framework guidance for security-sensitive behavior.

Pull `references/security-playbook.md` for focused audits of trust boundaries, auth, SSRF, secrets, injection, deserialization, and tenancy.

## Examples

Authorization review:
- Request: "Review this endpoint that lets users update invoices."
- Do: trace authentication, resource lookup, tenant ownership, permission checks, and tests for allowed and denied users.
- Watch: object ID access without ownership checks, admin-only behavior exposed to regular users, and checks done after mutation.

SSRF and external calls:
- Request: "Add user-provided callback URLs."
- Do: inspect URL parsing, allowlists, redirects, DNS/private IP handling, timeouts, and outbound client configuration.
- Watch: string prefix checks, redirect-to-internal-host bypasses, missing timeouts, and unsafe error logging.

Secrets handling:
- Request: "Review OAuth token storage."
- Do: inspect persistence, encryption or secret-manager usage, logs, exceptions, test fixtures, and admin/debug views.
- Watch: tokens in domain objects, serialized events, metrics labels, stack traces, and committed sample credentials.

## What To Watch

- Start with trust boundaries and attacker-controlled inputs.
- Prioritize exploitable paths over theoretical weakness.
- Security fixes need deny-path tests, not only happy-path tests.
- Do not invent crypto; use standard libraries or framework-supported primitives.
- State when risk depends on deployment config that is not visible in the repo.

## Good / Bad

Good:
- Identifies attacker-controlled input and protected assets.
- Traces authentication, authorization, validation, and side effects end to end.
- Explains exploitability, impact, affected boundary, and minimal fix.
- Requires deny-path tests for authorization and validation behavior.
- Separates confirmed vulnerabilities from missing evidence.

Bad:
- Treats generic hardening advice as a finding without exploit path.
- Checks authentication but misses resource ownership or tenant isolation.
- Logs or returns sensitive values while "fixing" errors.
- Recommends custom crypto or ad hoc token parsing.
- Assumes deployment protections exist without evidence.

## Output

Lead with exploitable findings, impact, affected boundary, recommended fix, and validation. State when evidence is insufficient.
Use `templates/security-review.md` for full security reviews when a structured report is useful.

## Definition Of Done

Security work is complete when:
- Trust boundaries, attacker-controlled inputs, protected assets, and authorization context are identified.
- Findings distinguish confirmed vulnerabilities from missing evidence or hardening suggestions.
- Each confirmed finding includes exploitability, impact, affected boundary, and minimal fix direction.
- Deny-path tests or validation are recommended for authorization, validation, tenant, and parsing changes.
- Dependency and deployment risks are scoped to visible evidence.
- Remaining unknowns are stated without assuming external protections exist.
