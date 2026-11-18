#!/bin/sh
# Install the Python Developer Agent Skill Suite.
#
# From a clone:
#   ./install.sh --host claude --global
#
# From the internet (project install into .agents/skills):
#   curl -fsSL https://github.com/bzdvdn/python-developer-ai-skill/releases/latest/download/install.sh | sh
#
# Run with --help for all options.
set -eu

REPO="bzdvdn/python-developer-ai-skill"
REF=""
HOST="agents"
SCOPE="project"
DEST=""
SRC=""
TMP=""

HOSTS="agents opencode claude codex kilo trae"

usage() {
    cat <<'EOF'
Install the Python Developer Agent Skill Suite.

Usage: install.sh [options]

Options:
  --host <name>    Target host: agents, opencode, claude, codex, kilo, trae, all
                   (default: agents, the vendor-neutral .agents/skills location)
  --global         Install into the host's user-level directory
  --project        Install into the current project (default)
  --dest <dir>     Explicit destination directory (overrides --host/--scope)
  --ref <ref>      Override the download ref: a branch, tag, or commit
                   (for example: --ref v0.1.4, --ref HEAD, --ref master)
  --repo <owner/repo>
                   Source repository (default: bzdvdn/python-developer-ai-skill)
  -h, --help       Show this help

Examples:
  ./install.sh --host claude --global
  ./install.sh --host opencode --project
  ./install.sh --dest ~/custom/skills
  curl -fsSL https://github.com/bzdvdn/python-developer-ai-skill/releases/latest/download/install.sh | sh -s -- --host codex --global
EOF
}

die() {
    printf 'error: %s\n' "$*" >&2
    exit 1
}

info() {
    printf '%s\n' "$*"
}

needs_value() {
    [ "$2" -ge 2 ] || die "$1 requires a value"
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --host)
            needs_value "$1" "$#"
            HOST=$2
            shift 2
            ;;
        --host=*)
            HOST=${1#*=}
            shift
            ;;
        --global)
            SCOPE=global
            shift
            ;;
        --project)
            SCOPE=project
            shift
            ;;
        --dest)
            needs_value "$1" "$#"
            DEST=$2
            shift 2
            ;;
        --dest=*)
            DEST=${1#*=}
            shift
            ;;
        --ref)
            needs_value "$1" "$#"
            REF=$2
            shift 2
            ;;
        --ref=*)
            REF=${1#*=}
            shift
            ;;
        --repo)
            needs_value "$1" "$#"
            REPO=$2
            shift 2
            ;;
        --repo=*)
            REPO=${1#*=}
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "unknown option: $1 (try --help)"
            ;;
    esac
done

case " $HOSTS all " in
    *" $HOST "*) ;;
    *) die "unknown host '$HOST' (choose: $HOSTS all)" ;;
esac

[ -n "$REPO" ] || die "--repo must not be empty"

script_root() {
    # Resolve the directory of a real script file. Piped installs ($0 is the
    # shell name) return an empty string and fall through to the download path.
    [ -f "$0" ] || return 0
    dir=$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd) || return 0
    if [ -f "$dir/install.sh" ] && [ -f "$dir/python-coder/SKILL.md" ]; then
        printf '%s\n' "$dir"
    fi
    return 0
}

resolve_latest_tag() {
    # Follow GitHub's /releases/latest redirect to its tag page. This avoids the
    # API rate limit and works with plain curl.
    redirect=$(curl -fsS -o /dev/null -w '%{redirect_url}' \
        "https://github.com/$REPO/releases/latest") || return 1
    tag=${redirect##*/}
    case "$tag" in
        ''|latest|releases|*/*) return 1 ;;
    esac
    printf '%s\n' "$tag"
    return 0
}

destination_for() {
    host=$1
    if [ "$SCOPE" = global ]; then
        [ -n "${HOME:-}" ] || die "HOME is not set (needed for --global)"
        case "$host" in
            agents) printf '%s\n' "$HOME/.agents/skills" ;;
            opencode) printf '%s\n' "${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills" ;;
            claude) printf '%s\n' "$HOME/.claude/skills" ;;
            codex) printf '%s\n' "${CODEX_HOME:-$HOME/.codex}/skills" ;;
            kilo) printf '%s\n' "$HOME/.kilo/skills" ;;
            trae) printf '%s\n' "$HOME/.trae/skills" ;;
        esac
    else
        case "$host" in
            agents) printf '%s\n' ".agents/skills" ;;
            opencode) printf '%s\n' ".opencode/skills" ;;
            claude) printf '%s\n' ".claude/skills" ;;
            codex) printf '%s\n' ".codex/skills" ;;
            kilo) printf '%s\n' ".kilo/skills" ;;
            trae) printf '%s\n' ".trae/skills" ;;
        esac
    fi
}

if [ -n "$DEST" ] && [ "$HOST" = all ]; then
    die "--dest cannot be combined with --host all"
fi

SRC=$(script_root)

if [ -z "$SRC" ]; then
    command -v curl >/dev/null 2>&1 || die "curl is required for a remote install"
    command -v tar >/dev/null 2>&1 || die "tar is required for a remote install"
    if [ -z "$REF" ]; then
        REF=$(resolve_latest_tag) \
            || die "could not resolve the latest release; pass --ref <tag|branch|commit>"
        info "Latest release: $REF"
    fi
    TMP=$(mktemp -d "${TMPDIR:-/tmp}/python-agent-skill.XXXXXX") || die "could not create a temp directory"
    trap 'rm -rf "$TMP"' EXIT HUP INT TERM
    info "Downloading $REPO@$REF ..."
    curl -fsSL "https://codeload.github.com/$REPO/tar.gz/$REF" -o "$TMP/suite.tar.gz" \
        || die "download failed (check --repo/--ref and network access)"
    mkdir -p "$TMP/src"
    tar -xzf "$TMP/suite.tar.gz" -C "$TMP/src" --strip-components=1 \
        || die "could not unpack the downloaded archive"
    SRC="$TMP/src"
    [ -f "$SRC/python-coder/SKILL.md" ] || die "downloaded archive does not look like this suite"
fi

install_into() {
    dest=$1
    mkdir -p "$dest" || die "cannot create destination: $dest"
    count=0
    for skill in "$SRC"/python-*/; do
        [ -d "$skill" ] || continue
        [ -f "${skill}SKILL.md" ] || continue
        name=$(basename "$skill")
        rm -rf "$dest/$name"
        cp -R "$skill" "$dest/$name" || die "failed to copy $name to $dest"
        count=$((count + 1))
    done
    [ "$count" -gt 0 ] || die "no skills found in $SRC"
    info "Installed $count skills into $dest"
}

if [ -n "$DEST" ]; then
    install_into "$DEST"
elif [ "$HOST" = all ]; then
    for host in $HOSTS; do
        install_into "$(destination_for "$host")"
    done
else
    install_into "$(destination_for "$HOST")"
fi

info "Restart the host or start a new session so it rescans skills."
