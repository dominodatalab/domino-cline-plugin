"""Audit tests for skill files — Rule 1 (auth), Rule 2 (hosts), Rule 3 (SDK).

These tests verify the static rules from the Skill Authoring Standards
(see CONTRIBUTING.md).  Rules 4 (verified endpoints) and 5 (smoke-tested
payloads) are not statically testable — they must be verified per-PR.
"""

import re
from pathlib import Path

import pytest

from .conftest import (EXTERNAL_CICD_FILES, REPO_ROOT, SKILLS_DIR,
                      SDK_REFERENCE_SKILLS, all_skill_main_files,
                      all_skill_md_files, skill_name_from_path)


# ═══════════════════════════════════════════════════════════════════════════
#  Frontmatter: every SKILL.md must have `name:` + `description:`
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.parametrize("path", all_skill_main_files(), ids=skill_name_from_path)
def test_skill_has_frontmatter(path: Path):
    """Every SKILL.md must start with YAML frontmatter containing
    `name:` and `description:` fields."""
    text = path.read_text()
    assert text.startswith("---"), f"{path.name}: missing opening frontmatter"
    assert "name:" in text[:500], f"{path}: missing `name:` in frontmatter"
    assert "description:" in text[:500], f"{path}: missing `description:` in frontmatter"


# ═══════════════════════════════════════════════════════════════════════════
#  Rule 1 — No deprecated API-key examples
# ═══════════════════════════════════════════════════════════════════════════

DEPRECATED_AUTH_RE = re.compile(
    r'(?:os\.environ\["DOMINO_USER_API_KEY"\]\s*=\s*"your-api-key"|'
    r'X-Domino-Api-Key:\s*"?(?:your-api-key|YOUR_API_KEY)"?)',
    re.IGNORECASE,
)


def _skip_if_exempt(path: Path):
    if path.name in EXTERNAL_CICD_FILES:
        pytest.skip("exempt: external CI/CD")
    skill = skill_name_from_path(path)
    if skill in SDK_REFERENCE_SKILLS:
        pytest.skip(f"exempt: SDK-reference skill ({skill})")


@pytest.mark.parametrize("path", all_skill_md_files(),
                         ids=lambda p: str(p.relative_to(SKILLS_DIR)))
def test_no_deprecated_auth_examples(path: Path):
    """Rule 1: No `DOMINO_USER_API_KEY = \"your-api-key\"` or
    `X-Domino-Api-Key: \"your-api-key\"` as active examples."""
    if path.name in EXTERNAL_CICD_FILES:
        pytest.skip("exempt: external CI/CD")
    relative = str(path.relative_to(REPO_ROOT))
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if DEPRECATED_AUTH_RE.search(line):
            if re.search(r'deprecated|Legacy|will be removed|Never use',
                         line, re.IGNORECASE):
                continue
            pytest.fail(
                f"{relative}:{i}: deprecated auth example — {line.strip()}")


@pytest.mark.parametrize("path", all_skill_md_files(),
                         ids=lambda p: str(p.relative_to(SKILLS_DIR)))
def test_no_placeholder_hosts(path: Path):
    """Rule 2: No `your-domino.com` (or variant) host placeholders."""
    relative = str(path.relative_to(REPO_ROOT))
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if re.search(r'your-domino', line, re.IGNORECASE):
            pytest.fail(
                f"{relative}:{i}: placeholder host — {line.strip()}")


@pytest.mark.parametrize("path", all_skill_md_files(),
                         ids=lambda p: str(p.relative_to(SKILLS_DIR)))
def test_no_sdk_outside_ref_skills(path: Path):
    """Rule 3: `from domino import Domino` only allowed in SDK-reference
    skills (domino-python-sdk, domino-data-sdk) and CI/CD files."""
    skill = skill_name_from_path(path)
    if skill in SDK_REFERENCE_SKILLS or path.name in EXTERNAL_CICD_FILES:
        pytest.skip(f"exempt: {skill if skill in SDK_REFERENCE_SKILLS else 'CI/CD'}")
    relative = str(path.relative_to(REPO_ROOT))
    for i, line in enumerate(path.read_text().splitlines(), 1):
        if re.search(r'from domino import Domino', line):
            pytest.fail(
                f"{relative}:{i}: python-domino SDK — {line.strip()}")


# ═══════════════════════════════════════════════════════════════════════════
#  Internal links
# ═══════════════════════════════════════════════════════════════════════════

INTERNAL_LINK_RE = re.compile(r'\]\(\./([^)\s]+)')


@pytest.mark.parametrize("path", all_skill_md_files(),
                         ids=lambda p: str(p.relative_to(SKILLS_DIR)))
def test_internal_links_resolve(path: Path):
    """Every `[text](./relative-path.md)` link must resolve to a real file."""
    parent = path.parent
    relative = str(path.relative_to(REPO_ROOT))
    for match in INTERNAL_LINK_RE.finditer(path.read_text()):
        target = match.group(1).rstrip(")")
        if target.startswith("#"):
            continue  # anchor-only refs are ok
        file_part = target.split("#")[0]
        if file_part and not (parent / file_part).resolve().is_file():
            pytest.fail(
                f"{relative}: broken link → ./{target} "
                f"(expected {parent / file_part})")


# ═══════════════════════════════════════════════════════════════════════════
#  Skill symlinks
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.skipif(not (Path.home() / ".cline" / "skills").is_dir(),
                     reason="~/.cline/skills/ not found")
def test_skill_symlinks_consistent():
    """Every symlink in ~/.cline/skills/ points to a real skills/ dir."""
    cline_skills = Path.home() / ".cline" / "skills"
    stale = []
    for sl in sorted(cline_skills.iterdir()):
        if sl.is_symlink() and not sl.resolve().is_dir():
            stale.append(sl.name)
    assert not stale, (
        f"Stale symlinks: {', '.join(stale)}.  "
        f"Re-run: for d in skills/*/; do "
        f"name=$(basename \"$d\"); "
        f"ln -sfn \"$(pwd)/$d\" ~/.cline/skills/\"$name\"; done")