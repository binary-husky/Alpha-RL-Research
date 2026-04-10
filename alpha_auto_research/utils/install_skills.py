"""Scan SKILL.md files in alpha_auto_research/skills and install them into .agents/skills."""

import os
import shutil
from pathlib import Path

_PACKAGE_SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
_AGENTS_SKILLS_DIR = Path.cwd() / ".agents" / "skills"


def install_skills() -> list[str]:
    """Copy all skill directories (containing SKILL.md) into .agents/skills/.

    Returns the list of installed skill names.
    """
    installed = []
    for skill_md in _PACKAGE_SKILLS_DIR.rglob("SKILL.md"):
        skill_dir = skill_md.parent
        skill_name = skill_dir.name
        dst = _AGENTS_SKILLS_DIR / skill_name

        # Remove old copy and replace
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(skill_dir, dst)
        installed.append(skill_name)

    if installed:
        print(f"[install_skills] Installed {len(installed)} skills: {', '.join(sorted(installed))}")
    return installed
