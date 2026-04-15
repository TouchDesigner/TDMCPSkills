#!/usr/bin/env python3
"""TDMCPSkills installer — install, uninstall, or check status of TouchDesigner skills for Claude Code.

Usage:
    python install.py install              # global install (~/.claude/skills/)
    python install.py install --project .  # project-local install
    python install.py uninstall            # global uninstall
    python install.py uninstall --project .
    python install.py status               # check global install
    python install.py status --project .
"""

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

MANIFEST_NAME = "td-skills-manifest.json"
SKILL_PREFIX = "td-"


def get_version():
    """Read version from VERSION file next to this script."""
    version_file = Path(__file__).resolve().parent / "VERSION"
    if not version_file.exists():
        print("Error: VERSION file not found next to install.py")
        sys.exit(1)
    return version_file.read_text().strip()


def get_source_skills():
    """Find all td-* skill directories in the source skills/ folder."""
    source_dir = Path(__file__).resolve().parent / "skills"
    if not source_dir.exists():
        print("Error: skills/ directory not found next to install.py")
        sys.exit(1)
    return sorted(
        d for d in source_dir.iterdir()
        if d.is_dir() and d.name.startswith(SKILL_PREFIX)
    )


def resolve_target(project_path):
    """Resolve the target .claude/skills/ directory."""
    if project_path:
        return Path(project_path).resolve() / ".claude" / "skills"
    return Path.home() / ".claude" / "skills"


def read_manifest(target_dir):
    """Read existing manifest from target, or None."""
    manifest_path = target_dir / MANIFEST_NAME
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def write_manifest(target_dir, version, skill_names):
    """Write manifest to target directory."""
    manifest = {
        "version": version,
        "installed": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "skills": skill_names,
    }
    manifest_path = target_dir / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


def remove_skills(target_dir, skill_names):
    """Remove listed skill directories from target."""
    removed = []
    for name in skill_names:
        skill_path = target_dir / name
        if skill_path.exists() and skill_path.is_dir():
            shutil.rmtree(skill_path)
            removed.append(name)
    return removed


def do_install(target_dir):
    """Install or upgrade skills to target directory."""
    version = get_version()
    source_skills = get_source_skills()
    skill_names = [d.name for d in source_skills]

    target_dir.mkdir(parents=True, exist_ok=True)

    # Remove existing install if manifest exists
    manifest = read_manifest(target_dir)
    if manifest:
        old_names = manifest.get("skills", [])
        old_version = manifest.get("version", "unknown")
        removed = remove_skills(target_dir, old_names)
        if removed:
            print(f"Removed {len(removed)} skills from previous install (v{old_version})")
    else:
        # First install — clean any stale td-* dirs
        stale = [
            d for d in target_dir.iterdir()
            if d.is_dir() and d.name.startswith(SKILL_PREFIX)
        ]
        if stale:
            for d in stale:
                shutil.rmtree(d)
            print(f"Cleaned {len(stale)} stale td-* directories")

    # Copy skills
    for source in source_skills:
        dest = target_dir / source.name
        shutil.copytree(source, dest)

    write_manifest(target_dir, version, skill_names)

    print(f"Installed TDMCPSkills v{version}")
    print(f"  {len(skill_names)} skills → {target_dir}")
    for name in skill_names:
        print(f"    {name}")


def do_uninstall(target_dir):
    """Uninstall skills from target directory."""
    manifest = read_manifest(target_dir)
    if not manifest:
        print(f"No TDMCPSkills installation found in {target_dir}")
        print("(no manifest file — nothing to uninstall)")
        return

    skill_names = manifest.get("skills", [])
    version = manifest.get("version", "unknown")

    removed = remove_skills(target_dir, skill_names)

    # Remove manifest
    manifest_path = target_dir / MANIFEST_NAME
    if manifest_path.exists():
        manifest_path.unlink()

    print(f"Uninstalled TDMCPSkills v{version}")
    print(f"  Removed {len(removed)} skills from {target_dir}")
    for name in removed:
        print(f"    {name}")

    leftover = [n for n in skill_names if n not in removed]
    if leftover:
        print(f"  {len(leftover)} skills were already missing:")
        for name in leftover:
            print(f"    {name}")


def do_status(target_dir):
    """Report install status."""
    manifest = read_manifest(target_dir)
    if not manifest:
        print(f"No TDMCPSkills installation found in {target_dir}")
        return

    version = manifest.get("version", "unknown")
    installed = manifest.get("installed", "unknown")
    skill_names = manifest.get("skills", [])

    # Check which are actually present
    present = [n for n in skill_names if (target_dir / n).is_dir()]
    missing = [n for n in skill_names if n not in present]

    print(f"TDMCPSkills v{version}")
    print(f"  Installed: {installed}")
    print(f"  Location:  {target_dir}")
    print(f"  Skills:    {len(present)}/{len(skill_names)} present")

    if missing:
        print(f"  Missing:   {', '.join(missing)}")


def main():
    parser = argparse.ArgumentParser(
        description="TDMCPSkills installer for Claude Code"
    )
    parser.add_argument(
        "command",
        choices=["install", "uninstall", "status"],
        help="Action to perform",
    )
    parser.add_argument(
        "--project",
        metavar="PATH",
        help="Install to project .claude/skills/ instead of global ~/.claude/skills/",
    )

    args = parser.parse_args()
    target_dir = resolve_target(args.project)

    if args.command == "install":
        do_install(target_dir)
    elif args.command == "uninstall":
        do_uninstall(target_dir)
    elif args.command == "status":
        do_status(target_dir)


if __name__ == "__main__":
    main()
