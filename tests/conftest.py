"""Shared fixtures and utilities for the domino-cline-plugin test suite."""

import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
MCP_DIR = REPO_ROOT / "mcp-servers" / "domino_mcp_server"

# ── Skills that are exempt from specific audit rules ──────────────────────

# SDK-reference skills — these exist to document the SDK, so their
# `from domino import Domino` / `import domino_data` lines are expected.
SDK_REFERENCE_SKILLS = {"domino-python-sdk", "domino-data-sdk"}

# External CI/CD — GitHub Actions cannot reach the in-cluster access-token
# sidecar, so API-key auth is the only viable path here.
EXTERNAL_CICD_FILES = {"REACT-CICD.md"}

# ── Helpers ───────────────────────────────────────────────────────────────


def all_skill_md_files() -> list[Path]:
    """Return every SKILL.md and supporting `.md` file under skills/."""
    return sorted(SKILLS_DIR.rglob("*.md"))


def all_skill_main_files() -> list[Path]:
    """Return only the top-level SKILL.md files."""
    return sorted(SKILLS_DIR.glob("*/SKILL.md"))


def skill_name_from_path(p: Path) -> str:
    """Extract the skill directory name from a path like skills/domino-jobs/SKILL.md."""
    return p.parent.name


def lines_of(path: Path) -> list[str]:
    """Return lines of a text file."""
    return path.read_text().splitlines()