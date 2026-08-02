#!/usr/bin/env python3
"""LLM-as-judge harness for skill eval scenarios.

Parses an eval scenario from ``evals/<skill>.md``, pairs it with a skill output,
and scores it against acceptance and anti-criteria using an LLM judge.

Dependency-free: uses only the standard library and an OpenAI-compatible
``/chat/completions`` endpoint.

Usage:
    python3 scripts/judge_eval.py --skill python-senior-architect \
        --scenario architect-review-clean-architecture --response response.md

Environment (any OpenAI-compatible endpoint works: OpenAI, DeepSeek, Mistral,
Ollama, vLLM, ...):
    LLM_API_KEY    required API key for the endpoint
    LLM_BASE_URL   required base URL, e.g. https://api.deepseek.com/v1 or
                   https://api.mistral.ai/v1 (or pass --base-url)
    LLM_MODEL      required judge model name (or pass --model)

Exit codes:
    0  verdict is pass
    1  verdict is fail (an acceptance criterion failed or an anti-criterion was hit)
    2  usage, parse, or judge availability error
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCENARIO_SPLIT_RE = re.compile(r"^## Scenario: (.+)$", re.MULTILINE)
BODY_SPLIT_RE = re.compile(r"^### (.+)$", re.MULTILINE)


def parse_scenarios(path: Path) -> dict[str, dict[str, str]]:
    """Return {scenario_id: {prompt, fixture, expected, acceptance, anti}}."""
    text = path.read_text(encoding="utf-8")
    parts = SCENARIO_SPLIT_RE.split(text)
    scenarios: dict[str, dict[str, str]] = {}
    for idx in range(1, len(parts), 2):
        scenario_id = parts[idx].strip()
        body = parts[idx + 1]
        scenarios[scenario_id] = parse_scenario_body(body)
    return scenarios


def _list_from(content: str) -> list[str]:
    items: list[str] = []
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        item = re.sub(r"^-\s*", "", line)
        item = re.sub(r"^\[[ xX]\]\s*", "", item).strip()
        if item:
            items.append(item)
    return items


def parse_scenario_body(body: str) -> dict[str, str]:
    data: dict[str, str] = {}
    parts = BODY_SPLIT_RE.split(body)
    for idx in range(1, len(parts), 2):
        heading = parts[idx].strip()
        content = parts[idx + 1].strip()
        if heading == "Prompt":
            data["prompt"] = content
        elif heading == "Repository Fixture":
            data["fixture"] = content
        elif heading == "Expected Behavior":
            data["expected"] = content
        elif heading == "Acceptance Criteria":
            data["acceptance"] = _list_from(content)
        elif heading == "Anti-Criteria":
            data["anti"] = _list_from(content)
    return data


def find_scenario(skill: str, scenario_id: str) -> dict[str, str]:
    path = ROOT / "evals" / f"{skill}.md"
    if not path.exists():
        raise SystemExit(f"eval file not found: {path}")
    scenarios = parse_scenarios(path)
    if scenario_id not in scenarios:
        raise SystemExit(f"scenario '{scenario_id}' not found in {path}")
    return scenarios[scenario_id]


def build_judge_prompt(skill: str, scenario_id: str, scenario: dict[str, str], response: str) -> str:
    acceptance = "\n".join(f"- {c}" for c in scenario.get("acceptance", [])) or "- (none)"
    anti = "\n".join(f"- {c}" for c in scenario.get("anti", [])) or "- (none)"
    return f"""You are an expert judge for a Python agent skill evaluation. Be strict and evidence-based. Never credit fabricated claims.

Skill under test: {skill}
Scenario: {scenario_id}

== USER PROMPT ==
{scenario.get("prompt", "(missing)")}

== REPOSITORY FIXTURE ==
{scenario.get("fixture", "(missing)")}

== EXPECTED BEHAVIOR ==
{scenario.get("expected", "(missing)")}

== SKILL OUTPUT TO JUDGE ==
{response}

== ACCEPTANCE CRITERIA ==
{acceptance}

== ANTI-CRITERIA ==
{anti}

Judge the output. For each acceptance criterion, mark pass, fail, or partial. For each
anti-criterion, mark whether the output violates it. Assess grounding: does the output
cite evidence from the fixture (files, imports, tests), or does it fabricate evidence?

Respond ONLY with a JSON object of this exact shape (no prose outside the JSON):
{{
  "acceptance": [{{"criterion": "...", "result": "pass|fail|partial", "note": "..."}}],
  "anti_criteria": [{{"criterion": "...", "violated": true|false, "note": "..."}}],
  "grounding": {{"fabricated_evidence": true|false, "note": "..."}},
  "summary": "one short paragraph",
  "verdict": "pass|fail"
}}
"""


def call_llm(messages: list[dict[str, str]], model: str, base_url: str, api_key: str) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {"model": model, "messages": messages, "temperature": 0}
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def parse_judge_output(content: str) -> dict:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("judge output contained no JSON object")
        return json.loads(match.group(0))


def compute_verdict(judged: dict) -> tuple[str, bool]:
    acceptance = judged.get("acceptance", [])
    anti = judged.get("anti_criteria", [])
    fabricated = bool(judged.get("grounding", {}).get("fabricated_evidence"))
    failures = [
        item.get("criterion")
        for item in acceptance
        if item.get("result") in ("fail", "partial")
    ]
    violations = [
        item.get("criterion")
        for item in anti
        if item.get("violated")
    ]
    if fabricated or violations or failures:
        return "fail", False
    return "pass", True


def main() -> int:
    parser = argparse.ArgumentParser(description="LLM-as-judge for skill eval scenarios.")
    parser.add_argument("--skill", required=True, help="Skill directory name, e.g. python-senior-architect.")
    parser.add_argument("--scenario", required=True, help="Scenario id from evals/<skill>.md.")
    parser.add_argument("--response", required=True, help="Path to the skill output file, or '-' for stdin.")
    parser.add_argument("--model", help="Judge model name (required unless LLM_MODEL is set).")
    parser.add_argument("--base-url", help="OpenAI-compatible base URL (required unless LLM_BASE_URL is set).")
    args = parser.parse_args()

    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("error: LLM_API_KEY is required (set it to the key your endpoint expects)", file=sys.stderr)
        return 2

    model = args.model or os.environ.get("LLM_MODEL")
    if not model:
        print("error: LLM_MODEL is required (set LLM_MODEL or pass --model)", file=sys.stderr)
        return 2
    base_url = args.base_url or os.environ.get("LLM_BASE_URL")
    if not base_url:
        print("error: LLM_BASE_URL is required (set LLM_BASE_URL or pass --base-url)", file=sys.stderr)
        return 2

    scenario = find_scenario(args.skill, args.scenario)
    if args.response == "-":
        response = sys.stdin.read()
    else:
        response = Path(args.response).read_text(encoding="utf-8")

    prompt = build_judge_prompt(args.skill, args.scenario, scenario, response)
    try:
        content = call_llm(
            [{"role": "user", "content": prompt}],
            model=model,
            base_url=base_url,
            api_key=api_key,
        )
    except Exception as exc:  # network, auth, or API errors
        print(f"error: judge call failed: {exc}", file=sys.stderr)
        return 2

    try:
        judged = parse_judge_output(content)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: could not parse judge output: {exc}", file=sys.stderr)
        print(content, file=sys.stderr)
        return 2

    verdict, ok = compute_verdict(judged)
    print(f"# Judge Result: {args.skill} / {args.scenario}")
    print(f"verdict: {verdict}")
    for item in judged.get("acceptance", []):
        print(f"- acceptance: {item.get('result')} | {item.get('criterion')}")
        if item.get("note"):
            print(f"    note: {item['note']}")
    for item in judged.get("anti_criteria", []):
        status = "VIOLATED" if item.get("violated") else "ok"
        print(f"- anti-criteria: {status} | {item.get('criterion')}")
    print(f"grounding: {'fabricated evidence' if judged.get('grounding', {}).get('fabricated_evidence') else 'grounded'}")
    print(f"summary: {judged.get('summary', '')}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
