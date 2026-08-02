# Security Playbook

Focused reference for security review of Python systems. Pull this in when a deep
audit of a specific risk area is needed. Every finding needs an exploit path, impact,
affected boundary, and minimal fix.

## Trust Boundaries

- Identify what is attacker-controlled: query params, bodies, headers, cookies,
  webhook payloads, uploaded files, queue messages, redirect targets.
- Identify protected assets: accounts, PII, billing data, credentials, admin actions.
- Identify where untrusted data crosses into trusted processing.

## Authentication And Authorization

- Auth must be enforced at the boundary where the route lives, not only in UI.
- Authorization checks must use resource ownership and tenant context, not just
  "user is logged in".
- Check-after-mutation is a defect; ownership checks happen before the mutation.
- Cover deny paths with tests, not only happy paths.
- Delegation of access (tokens, service identity) has a scope; verify it is granted
  narrowly and expires.

## Secrets

- Secrets must not appear in source, logs, errors, metrics labels, domain objects,
  or serialized events.
- Use standard library `secrets`/keyring or the platform secret manager; never custom crypto.
- Test fixtures and docs must not contain real credentials.
- Rotation must be possible; a secret without a rotation path is a single point of failure.

## Injection And Deserialization

- SQL and shell execution: no string interpolation; always parameterize.
- Deserialization: avoid `pickle`/`yaml.load` on untrusted data; prefer safe loaders
  and allowlists.
- Template/path injection: validate and restrict; resolve paths against a real root.
- Validate types and ranges at boundaries (numbers, lengths, code points) before they
  reach storage or framing code.

## SSRF And External Calls

- User-controlled URLs: validate scheme + host against an allowlist; block private IPs
  and link-local ranges; handle DNS rebinding.
- Reject prefix-only checks (they miss redirects and alternate host forms).
- Always set timeouts; configure the outbound client to disallow redirects when unsafe.
- Test the deny path: request to an internal host must fail.

## Cryptography And Key Management

- Use a vetted library (`cryptography`, platform KMS); never roll your own primitives.
- Hash/verify service passwords with a slow KDF (argon2/bcrypt/scrypt), not a fast hash.
- Encrypt at rest/in transit with current algorithms and named modes; key material should
  not be injected in defaults.
- Avoid token parsing by hand; use the framework's session/token machinery.

## Dependency Risk

- Pin and audit dependencies; check the lock file for known CVEs.
- Flag abandoned packages, transitive risk, and multiple overlapping clients.
- Scope dependency findings to visible evidence.
- Separate the audit (*does a CVE apply to this path?*) from the version bump.

## Tenancy

- Tenant isolation must hold at the data-access layer, not just middleware.
- Shared caches and queues must not leak tenant data: tenant scope must be part of
  the cache key and never shared across tenants.
- Multi-tenant boundaries are explicit and tested for cross-tenant access.

## Verification And Logging

- Log decisions and state transitions with correlation IDs; do not log request bodies
  or credentials.
- Ensure deny paths and boundary checks live under tests, not only in prose.

## Common Anti-Patterns

- "We use HTTPS so it is secure" without checking config.
- Custom crypto or ad hoc token parsing.
- Logging sensitive values while "fixing" an error.
- Assuming deployment protections exist without evidence.
- Sound returning an auth check after the mutation.
- A tenancy test that only checks the happy path, never a cross-tenant request.