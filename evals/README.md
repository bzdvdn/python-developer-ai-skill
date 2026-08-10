# Eval Scenarios

Golden scenarios for measuring skill quality. Use them to catch regressions when
editing a `SKILL.md` and to compare prompt versions.

## Format

One file per skill: `evals/<skill-name>.md`. Each file contains self-contained
scenario cards.

```markdown
## Scenario: <id>

### Prompt
<user request>

### Repository Fixture
<layout and code sketch; create a scratch copy to run against>

### Expected Behavior
- what the skill should produce or do

### Acceptance Criteria
- [ ] measurable pass conditions

### Anti-Criteria
- [ ] behaviors that must NOT appear
```

## Scoring

Run the skill against a scratch repository built from the fixture, then judge with
an LLM rubric or a human:

- Each acceptance criterion met: 1 point.
- Each anti-criterion hit: -1 point and a mandatory review.
- Additional quality bar: claims must be grounded in the fixture (files, imports,
  tests), not invented. A scenario fails if the skill fabricates evidence.

## Running

Scenarios are scored by an LLM-as-judge harness. Dependency-free; only an OpenAI-compatible
endpoint is required.

1. Run the skill against the scenario prompt and save its output to a file. The judge
   does not generate the skill output; it only scores it.
2. Judge a single scenario:

   ```bash
   export LLM_API_KEY=...
   python3 scripts/judge_eval.py --skill python-senior-architect \
       --scenario architect-review-clean-architecture --response out/response.md
   ```

   Use `--response -` to read the output from stdin.

3. Batch-judge a whole eval file or all skills:

   ```bash
   python3 scripts/run_evals.py --skill python-coder --responses out/
   python3 scripts/run_evals.py --responses out/
   python3 scripts/run_evals.py --responses out/ --report out/summary.json
   ```

   Pass `--report <path>` to write a JSON run summary (pass/fail/pending scenario ids
   and skipped count) alongside the console output.

   Response lookup: `out/<skill>/<scenario-id>.md`, then `out/<scenario-id>.md`.
   Missing responses are errors unless `--allow-missing` is set.

## Judge Configuration

Environment variables, all required except noted:

- `LLM_API_KEY` — key your endpoint expects (OpenAI-compatible). `OPENAI_API_KEY`
  is accepted as a fallback only.
- `LLM_BASE_URL` — OpenAI-compatible base URL. Any provider works, for example
  `https://api.deepseek.com/v1`, `https://api.mistral.ai/v1`,
  `https://api.openai.com/v1`, or `http://localhost:11434/v1` (Ollama).
- `LLM_MODEL` — judge model name on that endpoint, for example `deepseek-chat`,
  `mistral-large-latest`, or `gpt-4o-mini`.

The harness only speaks OpenAI-compatible `/chat/completions`; it never assumes
a provider. Missing `LLM_BASE_URL` or `LLM_MODEL` is a usage error (exit 2), not
a silent fallback to OpenAI.

## Verdict Rules

The judge marks each acceptance criterion `pass` / `fail` / `partial`, flags anti-criteria,
and checks grounding (fabricated evidence). A scenario fails when any criterion is
`fail`/`partial`, any anti-criterion is violated, or evidence is fabricated. Partial credit
is deliberately not awarded — partial is a fail, so the bar stays high.

Exit codes: `0` pass, `1` fail, `2` judge/usage error.

## Notes

- Fixtures are synthetic. Never present eval output as findings from a real repo.
- Prefer fixtures that expose the skill's specific job (routing, planning, review,
  layering) over generic code.
- Skill responses (`out/`) are LLM-generated and intentionally **not committed**;
  regenerate them per run and ignore the directory. The committed artifacts are the
  scenario definitions and the judge harness, not the model's answers. Scores depend
  on the judge model and endpoint, so treat a numeric score as a signal for a given
  `LLM_MODEL`, not as an absolute quality number.

## Limitations And Roadmap

- Fixtures are prose sketches, not checked-in code: the `Repository Fixture` section
  describes layout and responsibilities instead of materializing a runnable repo. The
  harness cannot currently build a scratch repository from a fixture, so runs stay
  semi-manual: generate the skill output against a fixture-derived scratch repo, then
  judge. Automating fixture materialization (a checked-in `fixtures/<skill>/<scenario>/`
  tree the judge can clone) is the planned next step.
- The judge is as good as the judge model and rubric; verdicts are relative, not
  absolute quality numbers.
