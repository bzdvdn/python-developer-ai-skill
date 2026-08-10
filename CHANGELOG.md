# Changelog

All notable changes to the Python Developer Agent Skill Suite are documented here.
Format follows Keep a Changelog. Versioning follows Semantic Versioning.

## [0.1.3] - 2026-08-11

### Changed

- `scripts/validate_suite.py` now cross-checks the SKILL frontmatter `version`
  against the latest `CHANGELOG.md` release and the README `Current version:` line,
  so a release bump can no longer drift across the suite.
- Shared `python-dependency-analyzer/scripts/pyast_utils.py` gained
  `framework_category()`: an import resolves to a single canonical keyword category
  by the most specific matching keyword, so `django.db.model` is `orm` and never
  also `web`. `architecture_report.py` and `check_layer_rules.py` both use this rule
  instead of each having its own top-level-first matching, which previously double-
  reported `django.db` under both `web` and `orm`.
- `scripts/run_evals.py` accepts `--report <path>` to write a JSON run summary
  (pass/fail/pending scenario ids and skipped count) for reproducible scoring.
- `evals/README.md` documents the JSON report and an explicit limitations/roadmap
  note: fixtures are prose sketches, so skill eval runs remain semi-manual until
  fixture materialization is automated.
- `README.md` clarified that `agents/` is optional and only
  `python-senior-architect` ships a reference `openai.yaml`; other skills point the
  host loader at `SKILL.md`.

### Added

- GitHub Actions workflow `.github/workflows/ci.yml`: runs
  `scripts/validate_suite.py --strict` and the unit-test suite on push and pull
  requests, with `PYTHONPYCACHEPREFIX` so no generated caches appear in the tree.
- Unit tests for `framework_category()` (`tests/test_pyast_utils.py`), for the
  changelog/README version cross-check, and for the single-category behavior in the
  layer-rule scanner and the architecture report.

## [0.1.1] - 2026-08-05

### Fixed

- `python-async-architect/scripts/detect_async_blocking.py`: no longer flags blocking
  calls that run off the event loop. A lambda or nested helper handed to an executor
  through a local variable (for example
  `fn = lambda: requests.get(url); await loop.run_in_executor(None, fn)`) was reported
  as a blocking call even though it is offloaded. Executor callables are now resolved
  through variable aliases (assignment before or after the call), and executor calls
  are matched by suffix (`.run_in_executor`, `.to_thread`) so `loop.run_in_executor`,
  `self._loop.run_in_executor`, and similar spellings are recognized, not only
  `asyncio.run_in_executor`. Direct synchronous calls are still flagged.
- Added six unit tests for the executor-offload false positives in
  `tests/test_detect_async_blocking.py`.

## [0.1.0] - 2026-08-02

First release. The suite is a set of composable agent skills for senior-level
Python development: one responsibility per skill, explicit handoff contracts,
deterministic tooling, a machine-checked concern ownership map, and LLM-as-judge
evals.

### Added

#### Skills

- Core skill set: `python-agent-orchestrator`, `python-senior-architect`,
  `python-coder`, `python-reviewer`, `python-testing`, `python-security`,
  `python-performance`, `python-production`, `python-dependency-analyzer`.
- Specialist skills: `python-architecture-scanner`, `python-data-architect`,
  `python-async-architect`.
- Every skill follows the open Agent Skills standard: a `SKILL.md` entry point with
  `name`, `description`, `metadata.short-description`, `version: 0.1.0`, and
  `license: MIT` frontmatter.

#### Handoff and routing

- `python-agent-orchestrator` routes work across the suite and defines the handoff
  contract.
- `templates/handoff.md` for all skills: objective, scope, out of scope, files,
  validation, risks, definition of done.

#### Templates

- `python-senior-architect/templates/`: `adr.md`, `architecture-review.md`,
  `code-review-summary.md`, `implementation-plan.md`, `incident-analysis.md`,
  `migration-plan.md`, `pr-review.md`, `risk-analysis.md`.
- `python-coder/templates/change-report.md`, `python-reviewer/templates/review-report.md`,
  `python-testing/templates/test-plan.md`, `python-security/templates/security-review.md`,
  `python-performance/templates/performance-report.md`,
  `python-production/templates/production-readiness.md`,
  `python-dependency-analyzer/templates/dependency-analysis.md`.
- `python-architecture-scanner/templates/`: `architecture-contract.md`, `scanner-report.md`.
- `python-data-architect/templates/`: `data-model-design.md`, `migration-review.md`.
- `python-async-architect/templates/`: `async-architecture-review.md`, `worker-design.md`.

#### References

- `python-senior-architect/references/`: `architecture-patterns.md`, `heuristics.md`,
  `inspection.md`, `refactoring-playbook.md`, `review-checklists.md`.
- `python-coder/references/python-practices.md`.
- `python-testing/references/`: `test-patterns.md`, `async-testing.md`.
- `python-security/references/security-playbook.md`.
- `python-performance/references/profiling-playbook.md`.
- `python-production/references/production-playbook.md`.
- `python-data-architect/references/persistence-patterns.md`.
- `python-async-architect/references/async-patterns.md`.

#### Deterministic tooling

- `python-dependency-analyzer/scripts/import_graph.py` — import graphs, cycles,
  layer violations, dependency health.
- `python-senior-architect/scripts/architecture_report.py` — architecture analysis
  report generation.
- `python-architecture-scanner/scripts/check_layer_rules.py` — layer-contract and
  forbidden-import enforcement for CI gates.
- `python-async-architect/scripts/detect_async_blocking.py` — blocking calls inside
  `async def` bodies.
- `scripts/sync_pyast_utils.py` — regenerates the bundled `pyast_utils` fallback
  copies across skills (`--check` verifies without writing).
- All scripts are dependency-free (standard library only).

#### Suite validation and evals

- `scripts/validate_suite.py` with `--strict` mode: unique skill names matching
  their directories, valid frontmatter, resolvable template/script/reference links,
  agreement between the suite document, the README, and the orchestrator skill list.
- Eval scenarios for all twelve skills under `evals/`, plus `evals/README.md`.
- LLM-as-judge harness: `scripts/judge_eval.py` (single skill/scenario) and
  `scripts/run_evals.py` (batch), OpenAI-compatible, dependency-free.

#### Examples

- `python-senior-architect/examples/`: `celery-migration-plan.md`,
  `django-layering-review.md`, `fastapi-hexagonal-review.md`.
- `examples/billing-feature-walkthrough.md` — end-to-end artifact example across skills.

#### Agent definitions

- `python-senior-architect/agents/openai.yaml` — OpenAI Agents SDK definition.

#### Documentation

- `README.md` — skill map, layout, usage, validation, testing, evals, roadmap.
- `INSTALL.md` — per-host installation guide (opencode, Claude Code, Codex CLI,
  Kilo Code, Trae) and the universal `.agents/skills/` option.
- `AGENTS.md` — repository conventions for contributing agents.
- `PYTHON_AGENT_SKILL_SUITE.md` — routing philosophy and recommended flows.
- `PYTHON_SENIOR_ARCHITECT_SKILL_DESIGN.md` — design rationale for the architect skill.
- `.gitignore` and `CHANGELOG.md`.

#### Testing

- Unit tests for all deterministic tooling, the suite validator, and the sync tool
  under `tests/` (stdlib `unittest`, no dependencies): import graph, architecture
  report, layer rules, async-blocking detection, eval judge, suite validator,
  fallback sync.
- Synthetic fixtures: `layered`, `cyclic`, and `async_blocking` repositories.

### Changed

- `PYTHON_SENIOR_ARCHITECT_SKILL_DESIGN.md`: added an explicit "Deterministic vs
  Agent Tooling" policy under the tool strategy, reconciling the stdlib-only
  constraint on shipped `scripts/` with the optional agent-facing analysis tools
  (`bandit`, `ruff`, `networkx`, `pydeps`, `import-linter`) — the latter are
  best-effort and must degrade gracefully, never fabricate a skipped check.
- `PYTHON_SENIOR_ARCHITECT_SKILL_DESIGN.md`: removed the inline review checklist
  (section 8), now a pointer to the canonical `references/review-checklists.md`,
  eliminating a second copy that could drift.
- Deepened the thin references: `python-performance/references/profiling-playbook.md`
  (measurement methodology, profiler-selection table, DB/async evidence, caching
  advice), `python-data-architect/references/persistence-patterns.md` (transactions
  and isolation, indexing, testing persistence, idempotency/outbox),
  `python-async-architect/references/async-patterns.md` (tasks and the event loop,
  timeouts/cancellation, testing async), `python-security/references/security-playbook.md`
  (cryptography, tenancy cache keys), and `python-production/references/production-playbook.md`
  (SLOs/capacity, change-and-rollback checklist).
- `scripts/validate_suite.py`: fixed inconsistent docstring item indentation.
- `.gitignore`: ignore `out/` for eval responses.
- Eval scores are judge-model-relative; skill responses (`out/`) are not committed.
  See `evals/README.md`.
- Single-sourced filesystem/AST helpers in `python-dependency-analyzer/scripts/pyast_utils.py`
  (`IGNORED_DIRS`, `FRAMEWORK_KEYWORDS`, `iter_python_files`, `module_name`,
  `module_set`, `imported_roots`, `parse_imports`, `resolve_relative_import`,
  `first_party_target`, `callable_name`, `resolve_top_level`); the import-graph,
  layer-rule, architecture-report, and async-blocking scripts import it instead of
  duplicating logic. De-duplicated the `IGNORED_DIRS` and keyword categories that
  were previously copied across scripts.
- Bundled `pyast_utils.py` fallbacks are no longer maintained by hand: they are
  produced by `scripts/sync_pyast_utils.py`, and `validate_suite.py` verifies the
  copies are byte-identical to the canonical module (so standalone skill installs
  work).
- Cross-skill scripts resolve the shared `pyast_utils` by walking up the install
  tree, then a bundled fallback, then `PYTHONPATH`, and exit with a clear message
  when it is genuinely unavailable.
- `FRAMEWORK_KEYWORDS` is now unambiguous: every keyword belongs to exactly one
  category. `aiohttp` is `web` only, `redis` is `cache` only, `pydantic`/`marshmallow`
  moved to a dedicated `validation` category, and `redis.asyncio` was removed.
  `validate_suite.py` enforces this uniqueness. `check_layer_rules.py` now matches
  full imports and dotted keywords (for example `django.db`, `google.cloud.storage`);
  `architecture_report.py` derives its infrastructure keywords from the shared map.
- Long `description` frontmatter fields were trimmed to one or two sentences focused
  on intent for better skill selection and routing; `short-description` is unchanged.
- De-duplicated `python-senior-architect/SKILL.md`: heuristics and review checklists
  live only in `references/`; the skill references them instead of inlining.
- Corrected the stale folder layout in `PYTHON_SENIOR_ARCHITECT_SKILL_DESIGN.md`
  (`import_graph.py` lives cross-skill in `python-dependency-analyzer/scripts/`).
- Disambiguated `concurrency` routing between `python-performance` (measure and
  profile) and `python-async-architect` (design the concurrency model and queue
  topology) in the orchestrator intent table and the performance skill description.

### Fixed

- `scripts/validate_suite.py` checks the README skill list, enforces a consistent
  `version` frontmatter, warns on `references/` headings duplicated inline in a
  `SKILL.md`, lists every cache directory instead of stopping at the first, validates
  the concern ownership map, enforces stdlib-only imports, verifies bundled
  `pyast_utils` copies, and enforces keyword-category uniqueness.
- `python-async-architect/scripts/detect_async_blocking.py`: removed the ineffective
  nested-function branch and clarified the docstring to match actual behavior.
- `python-architecture-scanner/scripts/check_layer_rules.py`: violations report the
  matched rule entry instead of a redundant layer name.
