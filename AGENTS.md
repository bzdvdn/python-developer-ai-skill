# AGENTS.md

Instructions for AI agents working in this repository. Keep skills consistent, validated, and single-sourced.

## Validation

Before finishing any change, run:

```bash
python3 scripts/validate_suite.py
```

The script checks: unique skill names matching their directory, valid frontmatter, resolvable template/script/reference links, agreement between the suite document and the orchestrator's skill list, stdlib-only imports across all scripts, and consistency of the concern ownership map.

## Skill Conventions

- Every skill is a directory named `python-<name>` with a `SKILL.md` entry point.
- `SKILL.md` frontmatter must contain `name` (matching the directory), `description`, and `metadata.short-description`.
- Templates are files in `templates/`. `SKILL.md` should reference the file, not reproduce it inline. Inline duplication drifts.
- Depth material goes in `references/` and is pulled on demand. `SKILL.md` stays lean.
- Deterministic tooling goes in `scripts/` and should be dependency-free. Shared filesystem/AST helpers live once in `python-dependency-analyzer/scripts/pyast_utils.py`; import them instead of duplicating them. Skills whose scripts import the shared module cross-skill ship a byte-identical bundled `pyast_utils.py` fallback in their own `scripts/` so a skill installed standalone still works. Regenerate those fallbacks with `python3 scripts/sync_pyast_utils.py`; do not hand-edit them. `validate_suite.py` enforces the stdlib-only rule, that every bundled fallback matches the canonical file, and that no framework keyword belongs to more than one `FRAMEWORK_KEYWORDS` category.
- Illustrative outputs go in `examples/`; never present them as real repository findings.

## Cross-Skill Rules

- One responsibility per skill. Do not let a skill silently absorb another skill's job. Overlapping specialists are split in the machine-checked concern map at `python-agent-orchestrator/references/concern-ownership.md`.
- Handoffs follow `templates/handoff.md`: objective, scope, out of scope, files, validation, risks, definition of done.
- When a skill references another skill's file, use the full relative path (for example `python-dependency-analyzer/scripts/import_graph.py`).
- Never commit secrets, credentials, or generated caches.

## Workflow

1. Check `git status` and `git diff` before editing.
2. Follow existing file style in the skill you touch.
3. Run `validate_suite.py` after structural changes (new skills, new templates, changed references).
4. Run Python scripts with `python3 -m py_compile` before finishing. Redirect the bytecode cache outside the tree so it does not trigger the suite's cache warning:
   ```bash
   PYTHONPYCACHEPREFIX=/tmp/opencode/pycache python3 -m py_compile scripts/validate_suite.py
   ```
   Then confirm with `python3 scripts/validate_suite.py --strict`.
5. Run the unit tests after changing any script in `scripts/` or any `python-*/scripts/`:
   ```bash
   PYTHONPYCACHEPREFIX=/tmp/opencode/pycache python3 -m unittest discover -s tests -v
   ```
   Follow the cache rule above so test runs do not leave `__pycache__` in the tree.
