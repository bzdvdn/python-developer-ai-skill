"""Tests for scripts/judge_eval.py scenario parsing and verdict logic."""

from __future__ import annotations

import unittest
from pathlib import Path

from tests._loader import load

ROOT = Path(__file__).resolve().parents[1]


class TestScenarioParsing(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("judge_eval")

    def test_real_eval_file_parses(self) -> None:
        scenarios = self.mod.parse_scenarios(ROOT / "evals" / "python-senior-architect.md")
        self.assertIn("architect-review-clean-architecture", scenarios)
        data = scenarios["architect-review-clean-architecture"]
        self.assertIn("prompt", data)
        self.assertIn("fixture", data)
        self.assertIn("acceptance", data)
        self.assertIn("anti", data)
        self.assertTrue(data["acceptance"])
        self.assertTrue(data["anti"])

    def test_all_eval_files_parse(self) -> None:
        for path in sorted((ROOT / "evals").glob("*.md")):
            if path.name == "README.md":
                continue
            scenarios = self.mod.parse_scenarios(path)
            self.assertTrue(scenarios, f"{path} has no scenarios")
            for scenario_id, data in scenarios.items():
                self.assertIn("acceptance", data, f"{path} / {scenario_id} missing acceptance")
                self.assertIn("anti", data, f"{path} / {scenario_id} missing anti-criteria")


class TestJudgePrompt(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("judge_eval")

    def test_prompt_includes_criteria_and_response(self) -> None:
        scenario = {"prompt": "p", "fixture": "f", "expected": "e", "acceptance": ["a1"], "anti": ["n1"]}
        prompt = self.mod.build_judge_prompt("python-testing", "scenario-x", scenario, "the response")
        self.assertIn("a1", prompt)
        self.assertIn("n1", prompt)
        self.assertIn("the response", prompt)
        self.assertIn("JSON", prompt)


class TestJudgeOutputParsing(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("judge_eval")

    def test_plain_json(self) -> None:
        content = '{"verdict": "pass", "acceptance": []}'
        self.assertEqual(self.mod.parse_judge_output(content)["verdict"], "pass")

    def test_fenced_json(self) -> None:
        content = '```json\n{"verdict": "fail"}\n```'
        self.assertEqual(self.mod.parse_judge_output(content)["verdict"], "fail")

    def test_json_embedded_in_text(self) -> None:
        content = 'Here you go: {"verdict": "pass"} -- done'
        self.assertEqual(self.mod.parse_judge_output(content)["verdict"], "pass")

    def test_malformed_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.mod.parse_judge_output("no json here")


class TestVerdictLogic(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load("judge_eval")

    def test_pass(self) -> None:
        judged = {
            "acceptance": [{"criterion": "c1", "result": "pass"}],
            "anti_criteria": [{"criterion": "n1", "violated": False}],
            "grounding": {"fabricated_evidence": False},
        }
        verdict, ok = self.mod.compute_verdict(judged)
        self.assertEqual(verdict, "pass")
        self.assertTrue(ok)

    def test_fail_on_partial(self) -> None:
        judged = {
            "acceptance": [{"criterion": "c1", "result": "partial"}],
            "anti_criteria": [],
            "grounding": {"fabricated_evidence": False},
        }
        self.assertFalse(self.mod.compute_verdict(judged)[1])

    def test_fail_on_anti_violation(self) -> None:
        judged = {
            "acceptance": [],
            "anti_criteria": [{"criterion": "n1", "violated": True}],
            "grounding": {"fabricated_evidence": False},
        }
        self.assertFalse(self.mod.compute_verdict(judged)[1])

    def test_fail_on_fabrication(self) -> None:
        judged = {
            "acceptance": [{"criterion": "c1", "result": "pass"}],
            "anti_criteria": [],
            "grounding": {"fabricated_evidence": True},
        }
        self.assertFalse(self.mod.compute_verdict(judged)[1])


if __name__ == "__main__":
    unittest.main()
