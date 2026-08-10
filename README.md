# Python Developer Agent Skill Suite

[![CI](https://github.com/bzdvdn/python-developer-ai-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/bzdvdn/python-developer-ai-skill/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/bzdvdn/python-developer-ai-skill)](LICENSE)
[![Release](https://img.shields.io/github/v/release/bzdvdn/python-developer-ai-skill)](CHANGELOG.md)
[![Stars](https://img.shields.io/github/stars/bzdvdn/python-developer-ai-skill)](https://github.com/bzdvdn/python-developer-ai-skill/stargazers)

Composable agent skills for senior-level Python development. Each skill owns one responsibility and hands off to others through explicit contracts, so no single skill tries to be architect, implementer, reviewer, tester, security auditor, performance engineer, and production engineer at once.

Current version: 0.1.3 (see [CHANGELOG.md](CHANGELOG.md)).

## Get Started In 60 Seconds

```bash
mkdir -p .agents/skills
cp -r python-*/ .agents/skills/
```

`.agents/skills/` is the vendor-neutral location recognized by opencode, Codex
CLI, Trae, and most other `SKILL.md`-based agents. Per-host paths (Claude Code,
Kilo Code, ...) are in [INSTALL.md](INSTALL.md). Then ask your agent, for
example:

- "Find circular imports in this repo"
- "Review this PR for architectural risks"
- "Plan how to add billing without coupling it to FastAPI handlers"

Each request routes to the smallest specialist skill chain and hands off through
explicit contracts.

## Why This Suite

- **One responsibility per skill** — no mega-prompt that tries to be architect,
  implementer, reviewer, and security auditor at once.
- **Progressive disclosure** — lean `SKILL.md` activation entry points, depth in
  `references/`, output contracts in `templates/`, so context stays small.
- **Evidence over opinion** — skills must ground claims in repository findings;
  the eval judge fails fabricated evidence.
- **Deterministic, dependency-free tooling** — import graphs, layer-rule gates,
  and async-blocking scans are stdlib-only Python that works in CI.
- **Machine-checked consistency** — `scripts/validate_suite.py --strict` verifies
  skill lists, versions, links, concern ownership, and byte-identical shared
  modules on every change.

## Skill Map

| Skill | Responsibility |
| --- | --- |
| `python-agent-orchestrator` | Routes work across the suite, defines handoff contracts |
| `python-senior-architect` | Architecture analysis, design, ADRs, plans, migration strategy |
| `python-coder` | Bounded implementation from a plan or clear request |
| `python-reviewer` | Code and PR review for correctness, regressions, maintainability |
| `python-testing` | Test strategy, fixtures, regression and contract coverage |
| `python-security` | Auth, secrets, injection, SSRF, dependencies, tenant isolation |
| `python-performance` | Profiling, database and async bottlenecks, caching, throughput |
| `python-production` | Deployment, observability, rollback, incidents, operational readiness |
| `python-dependency-analyzer` | Import graphs, cycles, layer violations, dependency health |
| `python-architecture-scanner` | Enforces layer contracts, forbidden-import rules, CI gates |
| `python-data-architect` | Persistence, data models, migrations, warehouses, pipelines |
| `python-async-architect` | Event loops, workers, queues, backpressure, messaging |

## Layout

Each skill lives in its own directory:

```
python-<name>/
├── SKILL.md          # instructions loaded by the host agent
├── references/       # depth material, pulled in on demand
├── templates/        # reusable output files
├── scripts/          # deterministic tooling
├── examples/         # illustrative outputs
└── agents/           # host-specific agent definitions
```

Top-level docs:

- `PYTHON_AGENT_SKILL_SUITE.md` — routing philosophy and recommended flows.
- `PYTHON_SENIOR_ARCHITECT_SKILL_DESIGN.md` — design rationale for the architect skill.
- `INSTALL.md` — per-host installation guide (opencode, Claude Code, Codex CLI, Kilo Code, Trae).
- `examples/billing-feature-walkthrough.md` — end-to-end artifact example across skills.
- `evals/` — golden scenarios for measuring skill quality.
- `scripts/validate_suite.py` — consistency validation.
- `CHANGELOG.md` — version history.

## Supported Hosts

| Host | Install |
| --- | --- |
| opencode | `.agents/skills/`, `.opencode/skills/`, or `~/.config/opencode/skills/` |
| Claude Code | `.agents/skills/`, `.claude/skills/`, or `~/.claude/skills/` |
| Codex CLI | `.agents/skills/`, `.codex/skills/`, or `~/.codex/skills/` |
| Kilo Code | `.kilo/skills/` or `%USERPROFILE%\.kilo\skills\` |
| Trae | `.agents/skills/`, `~/.trae/skills/`, or `%USERPROFILE%\.trae\skills\` |

See [INSTALL.md](INSTALL.md) for exact per-host commands.

## Usage

1. Load the `python-agent-orchestrator` skill when a request spans roles or the right skill is unclear.
2. Otherwise load the matching specialist skill directly.
3. Follow each skill's handoff contract when moving between skills.

To install the suite into a specific host (opencode, Claude Code, Codex CLI, Kilo
Code, Trae), see [INSTALL.md](INSTALL.md). An `agents/` folder may hold a
host-specific agent definition; only `python-senior-architect` ships one today
(the OpenAI Agents SDK reference `agents/openai.yaml`, see its header notes). For
every other skill, point the host's skill loader at the skill directory
`SKILL.md`.

A worked end-to-end example across skills lives in
[`examples/billing-feature-walkthrough.md`](examples/billing-feature-walkthrough.md).

## Validation

Run the suite consistency check:

```bash
python3 scripts/validate_suite.py --strict
```

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs the strict consistency
check and the unit tests on every push and pull request.

## Testing

Unit tests cover the deterministic tooling (import graph, architecture report, layer
rules, async-blocking detection, suite validator, and the eval judge). They use only
the standard library:

```bash
python3 -m unittest discover -s tests -v
```

Redirect the bytecode cache so test runs do not pollute the tree:

```bash
PYTHONPYCACHEPREFIX=/tmp/opencode/pycache python3 -m unittest discover -s tests
```

## Evals And LLM-As-Judge

`evals/` holds golden scenarios per skill. To score a skill output against a scenario:

1. Run the skill against the scenario prompt and save its output, for example `out/<skill>/<scenario>.md`.
2. Judge it with an LLM-as-judge (requires `LLM_API_KEY`):

```bash
python3 scripts/judge_eval.py --skill python-coder --scenario coder-bugfix-idempotent --response out/python-coder/coder-bugfix-idempotent.md
```

3. Batch-judge a whole eval file (or all skills) with `scripts/run_evals.py`:

```bash
python3 scripts/run_evals.py --skill python-senior-architect --responses out/
python3 scripts/run_evals.py --responses out/
```

Judge configuration via environment (any OpenAI-compatible endpoint works —
OpenAI, DeepSeek, Mistral, Ollama, vLLM, ...):

```bash
export LLM_API_KEY=...            # key your endpoint expects (required)
export LLM_BASE_URL=...           # e.g. https://api.deepseek.com/v1 (required)
export LLM_MODEL=...              # e.g. deepseek-chat (required)
```

`OPENAI_API_KEY` is accepted as a fallback key only. See `evals/README.md` for the format.

Individual tooling can be run directly:

```bash
python3 python-dependency-analyzer/scripts/import_graph.py <root>
python3 python-senior-architect/scripts/architecture_report.py <root> --domain-names <pkg...>
python3 python-architecture-scanner/scripts/check_layer_rules.py --config contract.json <root>
python3 python-async-architect/scripts/detect_async_blocking.py <root>
python3 scripts/sync_pyast_utils.py          # regenerate bundled shared-module fallbacks
python3 scripts/sync_pyast_utils.py --check  # verify fallbacks; exit non-zero on drift
```

The scripts share `python-dependency-analyzer/scripts/pyast_utils.py` for filesystem and
AST scanning (stdlib only). Cross-skill scripts resolve the canonical copy when the suite is
installed as a whole and fall back to a byte-identical bundled copy in their own skill, so a
skill installed on its own still runs; `scripts/validate_suite.py` enforces the stdlib-only
rule, that every bundled fallback matches the canonical module, and that no framework
keyword belongs to more than one category. Regenerate fallbacks with
`python3 scripts/sync_pyast_utils.py` rather than editing them by hand. Specialist overlap (for example performance vs
async architect, or dependency analyzer vs architecture scanner) is governed by a
machine-checked concern ownership map in
`python-agent-orchestrator/references/concern-ownership.md`.

The stdlib-only rule applies to the suite's shipped scripts for portability. When a
skill needs deeper evidence, its agent may call optional analysis tools that exist in
the shell (`bandit`, `ruff`, `networkx`, `pydeps`, `import-linter`, ...); those are
best-effort and must degrade gracefully — fall back to the suite scripts or repository
inspection rather than fabricating a tool's output. See the "Deterministic vs Agent
Tooling" policy in `PYTHON_SENIOR_ARCHITECT_SKILL_DESIGN.md`.

## Roadmap

- [x] Core skill set (orchestrator, architect, coder, reviewer, testing, security, performance, production, dependency-analyzer).
- [x] Optional specialists: architecture scanner, data architect, async architect.
- [x] Architect structure materialized (references, templates, scripts, examples, agent config).
- [x] Suite validation script.
- [x] Eval scenarios.
- [x] Deeper references for testing, security, performance, production.
- [x] Versioned releases and changelog.
- [ ] First release cut and tagged.

## License

MIT
