# Evals: python-agent-orchestrator

## Scenario: orchestrator-route-feature

### Prompt
Add recurring billing with webhooks and background reconciliation.

### Expected Behavior
- Classifies by intent and blast radius, not keyword count.
- Selects a minimal credible chain (e.g. Architect -> Security -> Coder -> Testing -> Production -> Reviewer).
- Produces a handoff with scope, out-of-scope, files, validation, risks, DoD.
- Does not route through every skill.

### Acceptance Criteria
- [ ] Chain is the shortest credible path for the risk.
- [ ] Handoff includes all sections from `templates/handoff.md`.
- [ ] Webhook trust and idempotency are named as risks.
- [ ] Stops routing where a clear owner exists.

### Anti-Criteria
- [ ] Routes through all skills by default.
- [ ] Sends implementation work to Architect or review to Coder.
- [ ] Produces a vague handoff.

## Scenario: orchestrator-stop-local

### Prompt
Fix the CLI crash when config is missing.

### Expected Behavior
- Routes to a localized chain (Coder -> Testing -> Reviewer) or stops at Coder.
- Does not involve Architect unless the fix exposes config-boundary redesign.

### Acceptance Criteria
- [ ] No Architect involvement for a local bug.
- [ ] The next concrete action is obvious and owned by one skill.

### Anti-Criteria
- [ ] Over-plans a trivial change.
- [ ] Keeps orchestrating after the next action is obvious.

## Scenario: orchestrator-conflict

### Prompt
Reviewer says the PR has a blocking authorization gap; Coder says it is fine.

### Expected Behavior
- States the conflict, chooses the safer reversible path (route back to Security/Architect), documents the trade-off.
- Security/data-integrity concerns override delivery convenience.

### Acceptance Criteria
- [ ] Conflict surfaced explicitly.
- [ ] Safer path chosen and documented.

### Anti-Criteria
- [ ] Silently picks one specialist's claim without escalation.
