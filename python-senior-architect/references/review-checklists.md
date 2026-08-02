# Review Checklists

Use as a structured prompt for architecture-focused PR and code reviews. Every finding needs evidence, impact, and a concrete fix direction.

## Architecture

- Clear module boundaries exist.
- Dependency direction is intentional.
- Domain, application, and infrastructure concerns are separated where useful.
- Framework code is contained at edges.
- New design fits current architecture or explicitly migrates it.
- No new cycles or hidden shared state.

## Naming

- Names reflect domain language.
- Package names communicate responsibility.
- Interfaces and services are named by capability, not mechanism.
- Avoid vague names like `manager`, `helper`, `utils` when responsibility is specific.

## Typing

- Public interfaces are typed.
- Boundary DTOs are explicit.
- Optional values and errors are modeled clearly.
- Type looseness is justified near dynamic or framework boundaries.

## Testing

- Domain rules have unit tests.
- Adapters have integration or contract tests.
- Migrations have rollback or compatibility checks.
- Async and messaging behavior covers idempotency and retries.
- Architecture-critical imports or contracts are enforceable.

## Security

- Auth and authorization are centralized or consistently applied.
- Secrets do not flow through logs or domain objects.
- Input validation happens at boundaries.
- External calls have timeouts and safe URL handling.
- Multi-tenant boundaries are explicit.

## Performance

- Hot paths avoid unnecessary network and database calls.
- Query patterns avoid N+1 behavior.
- Async code avoids blocking calls.
- Cache strategy has invalidation and observability.
- Backpressure and batching are considered.

## Maintainability

- Responsibilities are cohesive.
- Complexity is localized.
- New abstractions pay for themselves.
- Error handling is consistent.
- Configuration and wiring are understandable.

## Coupling

- Modules depend on stable contracts.
- Shared utilities do not become hidden architecture.
- Infrastructure dependencies do not spread inward.
- Cross-context calls are explicit.

## Cohesion

- Modules change for one dominant reason.
- Domain capabilities are not scattered across unrelated packages.
- Tests align with behavior ownership.

## API Design

- Public APIs are minimal, typed, and versionable.
- Failure modes are clear.
- Request and response contracts do not expose internals.
- Backward compatibility is considered.

## Documentation

- ADRs capture consequential decisions.
- README and docs reflect actual architecture.
- Operational assumptions are documented.
- Migration plans are discoverable.

## Observability

- Logs include correlation and business context.
- Metrics cover system and domain health.
- Traces cross process boundaries.
- Alerts map to user impact.

## Deployment

- Startup, migrations, and workers are coordinated.
- Rollback path exists.
- Environment configuration is explicit.
- Zero-downtime constraints are considered.

## Developer Experience

- Local setup supports architecture validation.
- Test commands are discoverable.
- Module ownership is understandable.
- Architectural rules can be checked automatically where practical.
