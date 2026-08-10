# Security Policy

Thanks for helping keep this suite safe.

## Reporting A Vulnerability

Please report security issues privately — do **not** open a public issue.

- **Preferred:** Create a security advisory via the repository's **Security →
  Report a vulnerability** tab (GitHub Security Advisories). This is private by
  default and lets us coordinate a fix before disclosure.
- **Fallback:** Email the maintainer with details.

Please include:

- The affected skill, script, or file and its version.
- A description of the issue and why it is a security problem.
- Steps to reproduce, or a minimal proof of concept.

## Scope

In scope:

- Security issues in the deterministic tooling (`scripts/**`,
  `python-*/scripts/**`): arbitrary code execution, unsafe path or AST handling,
  secret leakage, or tooling that can be tricked into misreporting a repository.
- Skill instructions that could cause an agent to leak secrets, approve
  destructive commands, or skip identity/authorization checks.
- The LLM-as-judge harness (`scripts/judge_eval.py`, `scripts/run_evals.py`):
  prompt-injection from skill outputs; API-key handling.

Not in scope (they are the *subject* of the suite, not its code):

- Vulnerabilities in a user's own application; the `python-security` skill exists
  to review those. Report them through the affected project's own process.

## Process

We aim to acknowledge reports within 48 hours and to triage vulnerabilities
with a severity assessment. Fixes land as a release and the advisory is
published after a fix is available.

## Safe Practices For Users

- Install skills only from sources you trust and review what you copy. This suite
  ships a `python3 scripts/validate_suite.py` consistency check — run it after
  copying the suite into another repository.
- The eval harness reads skills' outputs and sends them to the configured model
  endpoint; export `LLM_API_KEY` only in environments that should hold it.
- Never commit secrets. Treat any fixture or example that contains a credential
  as an error and report it under this policy.