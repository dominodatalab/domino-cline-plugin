#!/usr/bin/env python3
"""Pull the latest skills/agents/commands from domino-claude-plugin and
re-materialize them here as native Cline skills.

domino-cline-plugin is a standalone plugin (its own repo, meant to be shared
independently on GitHub), but its content is sourced from domino-claude-plugin
— the Claude Code plugin that remains the single source of truth for skill
instructions. Re-run this script after domino-claude-plugin changes upstream
to pick up those changes here.

What it does, per resource:
  - skills/*/SKILL.md   -> copy the whole directory (incl. bundled docs,
                            assets, references) to skills/<frontmatter-name>/,
                            renaming from the source's short dir name.
  - agents/*.md         -> wrap as skills/<name>/SKILL.md (already has a
                            matching `name:` field upstream).
  - commands/*.md       -> wrap as skills/<name>/SKILL.md (same).
  - mcp-servers/domino_mcp_server/  -> copied verbatim (the real Domino REST
                            API MCP server; not Cline-specific, just reused).

Deliberately NOT synced:
  - mcp-servers/skills_mcp_server/  -> built as a workaround for clients
    without native skill-routing (e.g. Continue+Qwen). Cline has native
    skills, so this would be a redundant second path to the same content.
  - hooks/, output-styles/ -> no Cline equivalent exists today.

Usage:
    python scripts/sync_from_domino_claude_plugin.py [--source PATH]

    --source PATH   Path to a local clone of domino-claude-plugin.
                     Defaults to a sibling checkout: ../domino-claude-plugin
"""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = REPO_ROOT.parent / "domino-claude-plugin"
DEST_SKILLS = REPO_ROOT / "skills"
DEST_MCP = REPO_ROOT / "mcp-servers" / "domino_mcp_server"
SYNC_STATE_FILE = REPO_ROOT / ".sync-source.json"


def _frontmatter_name(skill_md: Path) -> str | None:
    text = skill_md.read_text()
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    for line in text[3:end].splitlines():
        if line.strip().startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return None


def _source_commit(source: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def sync_skills(source: Path) -> list[str]:
    written = []
    for skill_dir in sorted((source / "skills").glob("*")):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        name = _frontmatter_name(skill_md)
        if not name:
            print(f"  SKIP {skill_dir.name}: no `name:` in frontmatter", file=sys.stderr)
            continue
        dest = DEST_SKILLS / name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(skill_dir, dest)
        written.append(name)
    return written


def sync_wrapped(source: Path, subdir: str) -> list[str]:
    written = []
    for md_file in sorted((source / subdir).glob("*.md")):
        name = _frontmatter_name(md_file)
        if not name:
            print(f"  SKIP {md_file.name}: no `name:` in frontmatter "
                  f"(commands/agents need `name:` added upstream)", file=sys.stderr)
            continue
        dest_dir = DEST_SKILLS / name
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(md_file, dest_dir / "SKILL.md")
        written.append(name)
    return written


def sync_mcp_server(source: Path) -> bool:
    src = source / "mcp-servers" / "domino_mcp_server"
    if not src.is_dir():
        return False
    if DEST_MCP.exists():
        # preserve a real .env across re-syncs — never overwrite credentials
        env_backup = None
        env_file = DEST_MCP / ".env"
        if env_file.exists():
            env_backup = env_file.read_text()
        shutil.rmtree(DEST_MCP)
        shutil.copytree(src, DEST_MCP, ignore=shutil.ignore_patterns(
            ".venv", "__pycache__", "*.pyc"))
        if env_backup is not None:
            (DEST_MCP / ".env").write_text(env_backup)
    else:
        shutil.copytree(src, DEST_MCP, ignore=shutil.ignore_patterns(
            ".venv", "__pycache__", "*.pyc"))
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not (source / "skills").is_dir():
        sys.exit(f"'{source}' doesn't look like a domino-claude-plugin checkout "
                  f"(no skills/ dir found). Pass --source /path/to/domino-claude-plugin.")

    DEST_SKILLS.mkdir(parents=True, exist_ok=True)

    print(f"Syncing from {source} ...")
    skills = sync_skills(source)
    agents = sync_wrapped(source, "agents")
    commands = sync_wrapped(source, "commands")
    mcp_ok = sync_mcp_server(source)

    commit = _source_commit(source)
    SYNC_STATE_FILE.write_text(
        f'{{\n'
        f'  "source_path": "{source}",\n'
        f'  "source_commit": "{commit}",\n'
        f'  "synced_at": "{datetime.now(timezone.utc).isoformat(timespec="seconds")}",\n'
        f'  "skills": {len(skills)},\n'
        f'  "agents": {len(agents)},\n'
        f'  "commands": {len(commands)}\n'
        f'}}\n'
    )

    print(f"  {len(skills)} skills, {len(agents)} agents, {len(commands)} commands "
          f"-> {DEST_SKILLS}")
    print(f"  domino_mcp_server: {'synced' if mcp_ok else 'NOT FOUND in source'}")
    print(f"  source commit: {commit}")
    print(f"\nReview with `git status` / `git diff` in {REPO_ROOT} before committing.")


if __name__ == "__main__":
    main()
