# Installing the Suite

The suite follows the open Agent Skills standard: every skill is a directory with a
`SKILL.md` entry point plus optional `references/`, `templates/`, `scripts/`,
`examples/`, and `agents/`. Installing for a host means copying the skill directory
into that host's skills location, then restarting (or starting a new session).

No host-specific wrapper is required: every skill already ships the `name` and
`description` frontmatter fields that all SKILL.md-based hosts read.

## One copy for most hosts

`.agents/skills/` is the vendor-neutral location recognized by opencode, Codex CLI,
Trae, and most other SKILL.md-based agents. A single copy there covers them:

```bash
mkdir -p .agents/skills
cp -r python-*/ .agents/skills/
```

Use this for shared projects. Use the per-host paths below for personal, cross-repo
installs or for hosts that do not read `.agents/skills/`.

## Per-host locations

| Host | Global | Project |
| --- | --- | --- |
| opencode | `~/.config/opencode/skills/` | `.opencode/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex CLI | `~/.codex/skills/` | `.codex/skills/` |
| Kilo Code | `~/.kilo/skills/` | `.kilo/skills/` |
| Trae | `~/.trae/skills/` | `.trae/skills/` |

### opencode

```bash
# Global (all projects)
mkdir -p ~/.config/opencode/skills
cp -r python-*/ ~/.config/opencode/skills/

# Project
mkdir -p .opencode/skills
cp -r python-*/ .opencode/skills/
```

opencode also discovers `.claude/skills/` and `.agents/skills/` in the repo and home
directory. Optionally restrict skills with `permission.skill` in `opencode.json`
(for example `"experimental-*": "ask"`).

### Claude Code

```bash
# Personal
mkdir -p ~/.claude/skills
cp -r python-*/ ~/.claude/skills/

# Project
mkdir -p .claude/skills
cp -r python-*/ .claude/skills/
```

The directory name must match the `name` frontmatter field and be lowercase
kebab-case; the suite already complies. Verify with `claude --list-skills` or
`/skills` inside a session. The plugin/marketplace route (`/plugin marketplace add`)
is not supported yet because this repository does not ship a `.claude-plugin`
manifest.

### Codex CLI

```bash
# User (respects $CODEX_HOME)
mkdir -p ~/.codex/skills
cp -r python-*/ ~/.codex/skills/

# Project
mkdir -p .codex/skills
cp -r python-*/ .codex/skills/
```

The repo-root `AGENTS.md` also serves as Codex CLI project context; a user-level
global file can go in `~/.codex/AGENTS.md`. The plugin route (`codex plugin
marketplace add`) is not supported yet because this repository does not ship a
`.codex-plugin` manifest.

### Kilo Code

```bash
# Global
mkdir -p ~/.kilo/skills
cp -r python-*/ ~/.kilo/skills/

# Project
mkdir -p .kilo/skills
cp -r python-*/ .kilo/skills/
```

Windows global path: `%USERPROFILE%\.kilo\skills\`. Kilo Code also reads compatible
directories such as `.claude/skills/` and `.agents/skills/`. Custom search paths can
be declared via `skills.paths` / `skills.urls` in `kilo.jsonc`.

### Trae

```bash
# Global (macOS/Linux)
mkdir -p ~/.trae/skills
cp -r python-*/ ~/.trae/skills/

# Project
mkdir -p .trae/skills
cp -r python-*/ .trae/skills/
```

Windows global path: `%userprofile%\.trae\skills\`. Trae also reads `.agents/skills/`
once enabled under Settings > Skills & Commands > Enable .agents Skills Directory;
`.trae/skills/` takes priority on name collisions.

## Verification

1. Restart the host (or start a new session) — skills are scanned at session start.
2. Confirm `SKILL.md` sits directly inside each `<name>/` directory and starts with
   `name` + `description` frontmatter.
3. Run the suite's own consistency check from the repository:

```bash
python3 scripts/validate_suite.py --strict
```

4. Load a skill and check the agent sees it (for example ask opencode which skills it
   has, or open `/skills` in Claude Code).
