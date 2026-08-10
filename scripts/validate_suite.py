#!/usr/bin/env python3
"""Validate the Python Agent Skill Suite consistency.

Checks:
1. Every skill directory ``python-<name>`` has a ``SKILL.md``.
2. Frontmatter contains ``name`` matching the directory, ``description``,
   and ``metadata.short-description``. Skill names are unique.
3. Every ``templates/``, ``scripts/``, and ``references/`` path referenced in a
   ``SKILL.md`` resolves to an existing file (relative to the skill directory
   or, for cross-skill full paths, relative to the repository root).
4. The skill list in ``PYTHON_AGENT_SKILL_SUITE.md``, ``README.md``, and the
   orchestrator's ``SKILL.md`` matches the directories present.
5. All skills share the same ``version`` frontmatter value, and that value
   matches the latest ``CHANGELOG.md`` release and the README's
   ``Current version:`` line, so release bumps cannot drift across the suite.
6. Warnings for generated caches left in the tree and for ``references/``
   headings duplicated inline in a ``SKILL.md``.
7. Every script under ``scripts/`` and ``python-*/scripts/`` imports only the
   standard library (plus suite-local modules), enforcing the dependency-free
   tooling rule and guarding the shared ``pyast_utils`` module.
8. The orchestrator's concern ownership map is consistent: one owner per
   concern, no unknown owners, every skill covered, and known overlap pairs
   disambiguated.
9. Every skill whose scripts import the shared ``pyast_utils`` module ships a
   byte-identical bundled copy so a skill installed standalone still works;
   a missing or drifted copy is an error.

Dependency-free. Run from the repository root: ``python3 scripts/validate_suite.py``
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
SKILL_TOKEN_RE = re.compile(r"`(python-[a-z-]+)`")
REF_RE = re.compile(r"((?:templates|scripts|references)/[A-Za-z0-9_./-]+|python-[a-z-]+/(?:templates|scripts|references)/[A-Za-z0-9_./-]+)")
HEADING_RE = re.compile(r"^## (.+)$", re.MULTILINE)
CACHE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
CHANGELOG_VERSION_RE = re.compile(r"^## \[([0-9]+\.[0-9]+\.[0-9]+)\]", re.MULTILINE)
README_VERSION_RE = re.compile(r"Current version:\s*([0-9]+\.[0-9]+\.[0-9]+)")

CONCERN_OWNERSHIP_REL = "python-agent-orchestrator/references/concern-ownership.md"
OWNERSHIP_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(python-[a-z][a-z0-9-]*)\s*\|\s*(.+?)\s*\|\s*$")

PYAST_UTILS_CANONICAL_REL = "python-dependency-analyzer/scripts/pyast_utils.py"

# Known overlap pairs that must stay split into distinct concerns.
OVERLAP_PAIRS = [
    ("python-performance", "python-async-architect"),
    ("python-dependency-analyzer", "python-architecture-scanner"),
    ("python-senior-architect", "python-data-architect"),
    ("python-senior-architect", "python-async-architect"),
]

# Suite-local modules that may be imported by scripts alongside the stdlib.
LOCAL_MODULES = {"pyast_utils", "judge_eval"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def parse_frontmatter(skill_md: Path) -> dict[str, str] | None:
    text = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    fm = match.group(1)
    fields: dict[str, str] = {}
    for key in ("name", "description", "version"):
        m = re.search(rf"^{key}:\s*(.+)$", fm, re.MULTILINE)
        if m:
            fields[key] = m.group(1).strip()
    m = re.search(r"^metadata:\s*$", fm, re.MULTILINE)
    if m:
        s = re.search(r"^\s+short-description:\s*(.+)$", fm[m.end():], re.MULTILINE)
        if s:
            fields["short-description"] = s.group(1).strip()
    return fields


def validate_skill(skill_dir: Path, report: Report) -> set[str]:
    name = skill_dir.name
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        report.error(f"{name}: missing SKILL.md")
        return {name}

    fields = parse_frontmatter(skill_md)
    if fields is None:
        report.error(f"{name}: invalid or missing frontmatter")
        return {name}

    if fields.get("name") != name:
        report.error(f"{name}: frontmatter name is '{fields.get('name')}', expected '{name}'")
    if not fields.get("description"):
        report.error(f"{name}: frontmatter missing description")
    if not fields.get("short-description"):
        report.error(f"{name}: frontmatter missing metadata.short-description")

    text = skill_md.read_text(encoding="utf-8")
    for ref in sorted(set(REF_RE.findall(text))):
        candidates = [
            skill_dir / ref,
            ROOT / ref,
        ]
        if not any(candidate.exists() for candidate in candidates):
            report.error(f"{name}: unresolved reference '{ref}'")

    return {name}


def validate_skill_list(report: Report) -> set[str]:
    dirs = {d.name for d in ROOT.glob("python-*/") if (d / "SKILL.md").exists()}

    suite_doc = ROOT / "PYTHON_AGENT_SKILL_SUITE.md"
    orchestrator = ROOT / "python-agent-orchestrator" / "SKILL.md"
    readme = ROOT / "README.md"

    suite_tokens = set(SKILL_TOKEN_RE.findall(suite_doc.read_text(encoding="utf-8"))) if suite_doc.exists() else set()
    orch_tokens = set(SKILL_TOKEN_RE.findall(orchestrator.read_text(encoding="utf-8"))) if orchestrator.exists() else set()
    readme_tokens = set(SKILL_TOKEN_RE.findall(readme.read_text(encoding="utf-8"))) if readme.exists() else set()

    if dirs != suite_tokens:
        report.error(
            "suite doc skill list mismatch with directories. "
            f"missing in doc: {sorted(dirs - suite_tokens)}; "
            f"doc-only: {sorted(suite_tokens - dirs)}"
        )
    routing_targets = dirs - {"python-agent-orchestrator"}
    if routing_targets != orch_tokens:
        report.error(
            "orchestrator skill list mismatch with directories. "
            f"missing in orchestrator: {sorted(routing_targets - orch_tokens)}; "
            f"orchestrator-only: {sorted(orch_tokens - routing_targets)}"
        )
    if dirs != readme_tokens:
        report.error(
            "README skill list mismatch with directories. "
            f"missing in README: {sorted(dirs - readme_tokens)}; "
            f"README-only: {sorted(readme_tokens - dirs)}"
        )
    return dirs


def validate_versions(report: Report, root: Path = ROOT) -> None:
    versions: dict[str, set[str]] = {}
    for skill_dir in root.glob("python-*/"):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        fields = parse_frontmatter(skill_md) or {}
        versions.setdefault(fields.get("version") or "<missing>", set()).add(skill_dir.name)
    if len(versions) > 1:
        for ver, names in sorted(versions.items()):
            report.error(f"version mismatch: '{ver}' -> {', '.join(sorted(names))}")
        return

    if len(versions) == 1:
        version = next(iter(versions))
        changelog = root / "CHANGELOG.md"
        if changelog.exists():
            match = CHANGELOG_VERSION_RE.search(changelog.read_text(encoding="utf-8"))
            if match and match.group(1) != version:
                report.error(
                    f"version mismatch: SKILL frontmatter '{version}' vs "
                    f"CHANGELOG latest '{match.group(1)}'"
                )
        readme = root / "README.md"
        if readme.exists():
            match = README_VERSION_RE.search(readme.read_text(encoding="utf-8"))
            if match and match.group(1) != version:
                report.error(
                    f"version mismatch: SKILL frontmatter '{version}' vs "
                    f"README 'Current version: {match.group(1)}'"
                )


def validate_duplication(skill_dir: Path, report: Report) -> None:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    skill_headings = set(HEADING_RE.findall(text))
    for ref in sorted(set(REF_RE.findall(text))):
        if "references/" not in ref:
            continue
        candidate = skill_dir / ref
        if not candidate.exists():
            candidate = ROOT / ref
        if not candidate.exists():
            continue
        overlap = set(HEADING_RE.findall(candidate.read_text(encoding="utf-8"))) & skill_headings
        if overlap:
            report.warn(
                f"{skill_dir.name}: headings in {ref} duplicated in SKILL.md: "
                + ", ".join(sorted(overlap))
            )


def check_caches(report: Report, root: Path = ROOT) -> None:
    found: set[Path] = set()
    for path in root.rglob("*"):
        rel = path.relative_to(root).parts
        for idx, part in enumerate(rel):
            if part in CACHE_DIRS:
                found.add(Path(*rel[: idx + 1]))
                break
    for cache in sorted(found):
        report.warn(f"generated cache present: {cache}")


def _allowed_imports() -> set[str] | None:
    if hasattr(sys, "stdlib_module_names"):
        return set(sys.stdlib_module_names) | set(sys.builtin_module_names) | LOCAL_MODULES
    return None


def validate_stdlib_only(report: Report, root: Path = ROOT) -> None:
    """Enforce that skill and suite scripts import only the standard library."""
    allowed = _allowed_imports()
    if allowed is None:
        report.warn("stdlib dependency check unavailable on this Python (<3.10); skipped")
        return

    scripts = sorted((root / "scripts").glob("*.py")) + sorted(root.glob("python-*/scripts/*.py"))
    for path in scripts:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            report.error(f"{path.relative_to(root)}: could not parse for stdlib-only check")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top not in allowed:
                        report.error(f"{path.relative_to(root)}: non-stdlib import '{top}'")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top = node.module.split(".")[0]
                    if top not in allowed:
                        report.error(f"{path.relative_to(root)}: non-stdlib import '{top}'")


def validate_concern_ownership(report: Report, root: Path = ROOT) -> None:
    """Enforce one-owner-per-concern and full skill coverage in the ownership map."""
    path = root / CONCERN_OWNERSHIP_REL
    if not path.exists():
        report.error(f"concern-ownership map missing: {CONCERN_OWNERSHIP_REL}")
        return

    skills = {d.name for d in root.glob("python-*/") if (d / "SKILL.md").exists()}
    rows: list[tuple[str, str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = OWNERSHIP_ROW_RE.match(line)
        if match:
            rows.append((match.group(1).strip(), match.group(2).strip(), match.group(3).strip()))

    if not rows:
        report.error(f"concern-ownership map has no ownership rows: {CONCERN_OWNERSHIP_REL}")
        return

    owners: dict[str, str] = {}
    seen_owners: set[str] = set()
    for concern, owner, boundary in rows:
        if concern in owners:
            report.error(f"concern-ownership: concern '{concern}' owned by both '{owners[concern]}' and '{owner}'")
        if owner not in skills:
            report.error(f"concern-ownership: unknown owner '{owner}' for concern '{concern}'")
        if not boundary:
            report.error(f"concern-ownership: concern '{concern}' has no boundary note")
        owners[concern] = owner
        seen_owners.add(owner)

    for skill in sorted(skills - seen_owners):
        report.error(f"concern-ownership: skill '{skill}' owns no concern")
    for left, right in OVERLAP_PAIRS:
        if left not in seen_owners:
            report.error(f"concern-ownership: overlap pair '{left}' is not disambiguated (no concern owner)")
        if right not in seen_owners:
            report.error(f"concern-ownership: overlap pair '{right}' is not disambiguated (no concern owner)")


def validate_framework_keywords(report: Report, root: Path = ROOT) -> None:
    """Enforce that a framework keyword belongs to at most one category, so the
    layer-rule scanner and architecture report produce one deterministic match."""
    canonical = root / PYAST_UTILS_CANONICAL_REL
    if not canonical.exists():
        return
    spec = importlib.util.spec_from_file_location("_pyast_utils_validate", canonical)
    if spec is None or spec.loader is None:
        report.error("framework keywords: could not load canonical pyast_utils for inspection")
        return
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # defensive: never crash the validator on a bad shared module
        report.error(f"framework keywords: canonical pyast_utils import failed: {exc}")
        return
    seen: dict[str, str] = {}
    for category, keywords in getattr(module, "FRAMEWORK_KEYWORDS", {}).items():
        for keyword in keywords:
            if keyword in seen:
                report.error(
                    f"FRAMEWORK_KEYWORDS: '{keyword}' in both '{seen[keyword]}' and '{category}'"
                )
            else:
                seen[keyword] = category


def validate_pyast_utils_copies(report: Report, root: Path = ROOT) -> None:
    """Enforce that bundled ``pyast_utils`` fallbacks exist and match the canonical copy.

    Skills whose scripts import the shared module ship a byte-identical bundled
    copy in their own ``scripts/`` directory so the skill works when installed
    standalone. A missing or drifted copy breaks that contract and is an error;
    ``python-dependency-analyzer/scripts/pyast_utils.py`` is the single source of truth.
    """
    canonical = root / PYAST_UTILS_CANONICAL_REL
    if not canonical.exists():
        report.error(f"canonical shared module missing: {PYAST_UTILS_CANONICAL_REL}")
        return
    canonical_bytes = canonical.read_bytes()
    for script in sorted(root.glob("python-*/scripts/*.py")):
        if script == canonical:
            continue
        text = script.read_text(encoding="utf-8")
        if "pyast_utils" not in text:
            continue
        skill = script.parent.parent.name
        if skill == "python-dependency-analyzer":
            continue
        bundled = script.parent / "pyast_utils.py"
        if not bundled.exists():
            report.error(
                f"{skill}/scripts: imports shared 'pyast_utils' but ships no bundled "
                "pyast_utils.py fallback (standalone installs would break)"
            )
        elif bundled.read_bytes() != canonical_bytes:
            report.error(
                f"{skill}/scripts/pyast_utils.py: bundled copy does not match "
                f"canonical {PYAST_UTILS_CANONICAL_REL}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Python Agent Skill Suite consistency.")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings too.")
    args = parser.parse_args()

    report = Report()
    names: set[str] = set()
    for skill_dir in sorted(ROOT.glob("python-*/")):
        names |= validate_skill(skill_dir, report)
        validate_duplication(skill_dir, report)

    validate_skill_list(report)
    validate_versions(report)
    validate_concern_ownership(report)
    validate_pyast_utils_copies(report)
    validate_framework_keywords(report)
    validate_stdlib_only(report)
    check_caches(report)

    for w in report.warnings:
        print(f"warning: {w}")
    for e in report.errors:
        print(f"error: {e}")

    if not report.errors:
        print(f"OK: {len(names)} skills validated")
    else:
        print(f"FAILED: {len(report.errors)} error(s), {len(report.warnings)} warning(s)")

    if report.errors or (args.strict and report.warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
