#!/usr/bin/env python3
"""Batch runner for LLM-as-judge skill evals.

Judges every scenario in one skill's eval file (or all skills) against responses
produced by running the skill. Reuses ``judge_eval`` for parsing and judging.

Usage:
    python3 scripts/run_evals.py --skill python-senior-architect --responses out/
    python3 scripts/run_evals.py --responses out/

Response lookup order per scenario ``<id>``:
    1. ``<responses>/<skill>/<id>.md``
    2. ``<responses>/<id>.md``

Environment: same as ``judge_eval`` (LLM_API_KEY / LLM_BASE_URL / LLM_MODEL).

Exit codes:
    0  all judged scenarios pass
    1  at least one judged scenario fails
    2  usage error, judge unavailable, or scenarios skipped due to missing responses
       (use --allow-missing to treat missing responses as skipped instead)

Pass ``--report <path>`` to also write a JSON summary (pass/fail/pending scenario
ids and skipped count) for reproducible scoring artifacts.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import judge_eval  # noqa: E402  (reuse parser + judge)


def collect_scenarios(skill: str | None) -> list[tuple[str, str, dict]]:
    if skill:
        paths = [ROOT / "evals" / f"{skill}.md"]
    else:
        paths = sorted((ROOT / "evals").glob("*.md"))
        paths = [p for p in paths if p.name != "README.md"]

    scenarios: list[tuple[str, str, dict]] = []
    for path in paths:
        skill_name = path.stem
        for scenario_id, data in judge_eval.parse_scenarios(path).items():
            scenarios.append((skill_name, scenario_id, data))
    return scenarios


def locate_response(responses_dir: Path, skill: str, scenario_id: str) -> Path | None:
    candidates = [
        responses_dir / skill / f"{scenario_id}.md",
        responses_dir / f"{scenario_id}.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch LLM-as-judge runner for skill evals.")
    parser.add_argument("--skill", default=None, help="Skill directory name. Default: all skills.")
    parser.add_argument("--responses", required=True, help="Directory containing skill output files.")
    parser.add_argument("--model", help="Judge model name (required unless LLM_MODEL is set).")
    parser.add_argument("--base-url", help="OpenAI-compatible base URL (required unless LLM_BASE_URL is set).")
    parser.add_argument("--parse-only", action="store_true", help="Only list scenarios and check responses; no LLM call.")
    parser.add_argument("--allow-missing", action="store_true", help="Treat missing responses as skipped, not an error.")
    parser.add_argument("--report", default=None, help="Optional path to write a JSON summary of the run.")
    args = parser.parse_args()

    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not args.parse_only and not api_key:
        print("error: LLM_API_KEY is required (set it to the key your endpoint expects)", file=sys.stderr)
        return 2

    model = args.model or os.environ.get("LLM_MODEL")
    base_url = args.base_url or os.environ.get("LLM_BASE_URL")
    if not args.parse_only:
        if not model:
            print("error: LLM_MODEL is required (set LLM_MODEL or pass --model)", file=sys.stderr)
            return 2
        if not base_url:
            print("error: LLM_BASE_URL is required (set LLM_BASE_URL or pass --base-url)", file=sys.stderr)
            return 2

    responses_dir = Path(args.responses).resolve()
    if not responses_dir.is_dir():
        print(f"error: responses directory not found: {responses_dir}", file=sys.stderr)
        return 2

    scenarios = collect_scenarios(args.skill)
    results: list[dict] = []
    skipped = 0

    for skill, scenario_id, _data in scenarios:
        response_path = locate_response(responses_dir, skill, scenario_id)
        if response_path is None:
            if args.allow_missing:
                skipped += 1
                print(f"skip: {skill} / {scenario_id} (no response)")
                continue
            print(f"error: no response for {skill} / {scenario_id} (missing: {responses_dir}/{skill}/{scenario_id}.md)")
            return 2
        response = response_path.read_text(encoding="utf-8")

        if args.parse_only:
            results.append({"skill": skill, "scenario": scenario_id, "verdict": "pending", "response": str(response_path)})
            continue

        prompt = judge_eval.build_judge_prompt(skill, scenario_id, _data, response)
        try:
            content = judge_eval.call_llm(
                [{"role": "user", "content": prompt}],
                model=model,
                base_url=base_url,
                api_key=api_key,
            )
        except Exception as exc:
            print(f"error: judge call failed for {skill} / {scenario_id}: {exc}", file=sys.stderr)
            return 2
        judged = judge_eval.parse_judge_output(content)
        verdict, _ok = judge_eval.compute_verdict(judged)
        results.append({"skill": skill, "scenario": scenario_id, "verdict": verdict})

    # Report
    failed = [r for r in results if r["verdict"] == "fail"]
    passed = [r for r in results if r["verdict"] == "pass"]
    pending = [r for r in results if r["verdict"] == "pending"]

    print("\n# Eval Run Summary")
    print(f"skills: {len({r['skill'] for r in results})}  scenarios: {len(results)}  "
          f"pass: {len(passed)}  fail: {len(failed)}  skipped: {skipped}")
    if pending:
        print("\nPending (parse-only):")
        for r in pending:
            print(f"- {r['skill']} / {r['scenario']}  ({r['response']})")
    if failed:
        print("\nFailed:")
        for r in failed:
            print(f"- {r['skill']} / {r['scenario']}")

    if args.report:
        summary = {
            "skills": sorted({r["skill"] for r in results}),
            "scenarios": len(results),
            "pass": [r["scenario"] for r in passed],
            "fail": [r["scenario"] for r in failed],
            "pending": [r["scenario"] for r in pending],
            "skipped": skipped,
        }
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(f"report: {report_path}")

    if failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
