---
name: python-reviewer
version: 0.1.1
license: MIT
description: Use for Python code review and PR review focused on correctness, regressions, maintainability, typing, tests, API behavior, and integration risk. This skill prioritizes findings with file references and does not rewrite code unless explicitly asked.
metadata:
  short-description: Review Python changes and PRs
---

# Python Reviewer

## Mission

Review Python code like a senior maintainer. Find real bugs, regressions, missing tests, maintainability risks, and unsafe assumptions. Keep findings evidence-based and prioritized.

## Activation

Use for:
- "Review this PR/change/diff."
- Pre-merge quality checks.
- Regression risk analysis.
- API compatibility review.
- Test coverage review.

Do not use for:
- Initial architecture design.
- Large implementation.
- Deep security or performance audit unless asked.

## Workflow

1. Inspect `git status` and relevant diff.
2. Read changed files and nearby code.
3. Understand expected behavior.
4. Check tests and validation.
5. Identify findings by severity.
6. Provide file and line references.
7. Separate blockers from suggestions.
8. Mention residual risk and unrun validation.

## Checklist

- Correctness: edge cases, error paths, invariants, state transitions, concurrency, idempotency.
- Compatibility: API contracts, migrations, config, serialization, client behavior.
- Tests: missing regression tests, wrong test layer, brittle mocks, untested failure paths.
- Typing: public contracts, unsafe `Any`, optional handling, protocol mismatch.
- Maintainability: unclear naming, large functions, hidden coupling, duplicated logic.
- Architecture: layer violations, framework leakage, dependency direction, circular imports.
- Security: auth gaps, input validation, secrets, unsafe deserialization, injection, SSRF.
- Performance: N+1 queries, blocking async code, unbounded loops, missing timeouts.
- Operations: logging, metrics, rollback, deploy order, migration safety.

## Output Rules

- Findings first, ordered by severity.
- Include file and line references.
- Explain impact and concrete fix direction.
- Keep summary short.
- Say explicitly when no findings are found.
- Do not fill space with low-value praise.
- Use `templates/review-report.md` for full reviews when a structured report is useful.

## Examples

Correctness review:
- Request: "Review this PR that changes order cancellation."
- Do: inspect the diff, caller expectations, state transitions, database updates, and tests around cancelled, shipped, and already-refunded orders.
- Watch: new invalid states, non-idempotent retries, partial commits, and missing regression tests for edge cases.

API compatibility review:
- Request: "Review this response schema change."
- Do: compare old and new contracts, serialization behavior, clients, OpenAPI docs, and migration notes.
- Watch: renamed fields, changed nullability, error shape drift, and unversioned breaking changes.

Test review:
- Request: "Review these new tests."
- Do: check whether tests fail on the old bug, cover the right layer, and avoid coupling to private implementation.
- Watch: mocks that assert implementation choreography instead of behavior, fixtures that hide important setup, and missing negative cases.

## What To Watch

- Lead with issues that can break users, data, security, operations, or maintainability.
- Do not report speculative style preferences as findings.
- Every finding needs evidence, impact, and a concrete fix direction.
- If evidence is incomplete, state the residual risk instead of guessing.
- A clean review still mentions meaningful validation gaps.

## Good / Bad

Good:
- Starts with blocking findings, ordered by severity.
- References concrete files and lines.
- Explains why the issue matters to users, data, API contracts, tests, or operations.
- Suggests a practical fix direction without rewriting the PR.
- Says "no findings" when the review did not uncover real issues.

Bad:
- Leads with summary or praise while hiding findings later.
- Reports style preferences as defects.
- Uses vague language like "could be better" without impact.
- Flags code without checking surrounding behavior or tests.
- Invents risk that is not supported by the diff or repository evidence.

## Template

```markdown
# Findings
- [Severity] `path:line` - Issue, impact, and suggested fix.

# Open Questions
- ...

# Residual Risk
- ...

# Validation
- ...
```

## Definition Of Done

Review is complete when:
- The relevant diff, changed files, nearby code, and tests were inspected.
- Findings are ordered by severity and include file references, impact, evidence, and fix direction.
- Suggestions are clearly separated from blockers.
- Missing tests and unrun validation are called out.
- If no findings are found, the review says so explicitly and names residual risk.
- The response does not include speculative style preferences as defects.
