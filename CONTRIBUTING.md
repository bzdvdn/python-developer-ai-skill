# Contributing

Thanks for considering a contribution to the Python Developer Agent Skill Suite.

This suite is both a set of prompts (the `SKILL.md` files and their references)
and a small Python codebase (the deterministic tooling under `scripts/`). Keep
contributions to the same standards as the existing code: single-sourced,
validated, and consistent.

## Before You Start

Read [`AGENTS.md`](AGENTS.md) — it is the authoritative contributor contract and
is enforced by `scripts/validate_suite.py`. In particular:

- Every skill is a directory named `python-<name>` with `SKILL.md` as its entry
  point and valid `name`, `description`, and `metadata.short-description`
  frontmatter.
- Templates live in `templates/`, depth material in `references/`, deterministic
  tooling in `scripts/`. Do not reproduce template or reference content inline in
  a `SKILL.md`; reference the file instead.
- Prepared scripts import only the standard library. Shared filesystem/AST
  helpers live once in `python-dependency-analyzer/scripts/pyast_utils.py`;
  bundled fallbacks are byte-identical copies regenerated with
  `scripts/sync_pyast_utils.py`, never hand-edited.
- Never commit secrets, credentials, or generated caches.

## Local Validation

```bash
# Consistency (skills, frontmatter, links, versions, concern map, stdlib-only,
# byte-identical shared-module fallbacks, cache hygiene):
python3 scripts/validate_suite.py --strict

# Unit tests for the deterministic tooling and the validator:
PYTHONPYCACHEPREFIX=/tmp/opencode/pycache python3 -m unittest discover -s tests -v
```

Redirect the bytecode cache outside the tree so test runs do not pollute the
repository (the validator warns on any `__pycache__` left behind).

## Types Of Contributions

### New skill or skill change

1. Keep one responsibility per skill. Check the machine-checked concern map at
   `python-agent-orchestrator/references/concern-ownership.md`; if your change
   would let a skill absorb another skill's job, it will fail validation.
2. Update the skill list in `README.md`, `PYTHON_AGENT_SKILL_SUITE.md`, and the
   orchestrator's `SKILL.md` together — `validate_suite.py` treats a mismatch as
   an error.
3. Add a golden scenario under `evals/<skill>.md` for new behavior, and use the
   LLM-as-judge harness (`scripts/judge_eval.py` / `scripts/run_evals.py`) to
   score it.

### Tooling change (import graph, layer rules, async blocker, validator, ...)

1. Keep it dependency-free (stdlib only).
2. Add or update a unit test under `tests/`. Fixtures live in `tests/fixtures/`.
3. If you touch `pyast_utils.py`, regenerate the bundled fallbacks and update the
   tests: `python3 scripts/sync_pyast_utils.py` and `--check` to verify.

### Documentation

Update the skill's `SKILL.md`, `references/`, `templates/`, and the top-level
docs in the same change to avoid drift. The validator warns when a
`references/` heading is duplicated inline in a `SKILL.md`.

## Definition Of Done

A contribution is complete when all of the following hold:

- `python3 scripts/validate_suite.py --strict` passes.
- `python3 -m unittest discover -s tests` passes.
- No generated caches or artifacts are left in the tree.
- `CHANGELOG.md` has an entry describing the user-visible change.
- The change follows the suite's single-responsibility and
  single-source-of-truth rules.