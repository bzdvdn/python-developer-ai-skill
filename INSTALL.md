# Installing the Suite

The suite follows the open Agent Skills standard: every skill is a directory with a
`SKILL.md` entry point plus optional `references/`, `templates/`, `scripts/`,
`examples/`, and `agents/`. Installing for a host means copying the skill directory
into that host's skills location, then restarting (or starting a new session).

No host-specific wrapper is required: every skill already ships the `name` and
`description` frontmatter fields that all SKILL.md-based hosts read.

## Quick install (no clone)

Each GitHub release publishes `install.sh` and `install.ps1` as release assets,
and the installer from a release installs that same release. The
`/releases/latest/download/...` URLs below pick the newest release, so nothing
is fetched from the `master` branch. Use `--ref` (`-Ref` on Windows) to install
a different branch, tag, or commit from within an installer.

Linux, macOS, and other Unix shells (project install into `.agents/skills`):

```bash
curl -fsSL https://github.com/bzdvdn/python-developer-ai-skill/releases/latest/download/install.sh | sh
```

Choose a host and scope with arguments:

```bash
# Global install for Claude Code (~/.claude/skills)
curl -fsSL https://github.com/bzdvdn/python-developer-ai-skill/releases/latest/download/install.sh | sh -s -- --host claude --global

# One copy into every supported host location in the current project
curl -fsSL https://github.com/bzdvdn/python-developer-ai-skill/releases/latest/download/install.sh | sh -s -- --host all

# Explicit directory, or a pinned ref instead of the latest release
curl -fsSL https://github.com/bzdvdn/python-developer-ai-skill/releases/latest/download/install.sh | sh -s -- --dest ~/tools/skills
curl -fsSL https://github.com/bzdvdn/python-developer-ai-skill/releases/latest/download/install.sh | sh -s -- --ref v0.1.5

# Or pin the installer asset itself (it installs its own release)
curl -fsSL https://github.com/bzdvdn/python-developer-ai-skill/releases/download/v0.1.5/install.sh | sh
```

From a clone, call the script directly: `./install.sh --host opencode --global`.
Run `./install.sh --help` for all options. The script is POSIX `sh`, needs only
`curl` and `tar`, and replaces only the suite's own `python-*` directories.

Windows PowerShell (project install into `.\.agents\skills`):

```powershell
irm https://github.com/bzdvdn/python-developer-ai-skill/releases/latest/download/install.ps1 | iex
```

With options, create a script block so parameters are passed correctly:

```powershell
& ([scriptblock]::Create((irm https://github.com/bzdvdn/python-developer-ai-skill/releases/latest/download/install.ps1))) -HostName claude -Global
& ([scriptblock]::Create((irm https://github.com/bzdvdn/python-developer-ai-skill/releases/latest/download/install.ps1))) -HostName all
& ([scriptblock]::Create((irm https://github.com/bzdvdn/python-developer-ai-skill/releases/latest/download/install.ps1))) -Destination C:\tools\skills
```

From a clone: `.\install.ps1 -HostName codex -Global`. Requires Windows
PowerShell 5.1 or later.

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
`/skills` inside a session.

The plugin route is supported too: this repository ships
`.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json`, so

```bash
/plugin marketplace add bzdvdn/python-developer-ai-skill
/plugin install python-developer-ai-skill@python-developer-ai-skill
```

loads all twelve skills as a plugin (the plugin manifest lists each
`python-<name>` directory as a skill). `cp -r` to `.claude/skills/` remains the
fallback for hosts or versions without the plugin loader.

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
global file can go in `~/.codex/AGENTS.md`.

The plugin route is supported too: this repository ships `.codex-plugin/plugin.json`,
so

```bash
codex plugin marketplace add bzdvdn/python-developer-ai-skill
codex plugin add python-developer-ai-skill@python-developer-ai-skill
```

loads all twelve skills as a plugin. `cp -r` to `.codex/skills/` remains the
fallback for CLI versions without the plugin loader.

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
