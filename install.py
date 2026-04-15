#!/usr/bin/env python3
"""TDMCPSkills installer — install, uninstall, or check status of TouchDesigner skills for Claude Code.

Dual-mode: when run from the TDMCPSkills repo (skills/ dir present), installs from local files.
When run standalone from any directory, fetches the latest from GitHub automatically.

Usage:
    python install.py install              # global install (~/.claude/skills/)
    python install.py install --project .  # project-local install
    python install.py uninstall            # global uninstall
    python install.py uninstall --project .
    python install.py status               # check install + available updates
    python install.py status --project .
"""

import argparse
import io
import json
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

MANIFEST_NAME = "td-skills-manifest.json"
SKILL_PREFIX = "td-"
DEFAULT_REPO = "TouchDesigner/TDMCPSkills"
DEFAULT_BRANCH = "main"


# ---------------------------------------------------------------------------
# Source detection
# ---------------------------------------------------------------------------

def detect_local_source():
    """Return the repo root Path if skills/ and VERSION exist next to this script, else None."""
    script_dir = Path(__file__).resolve().parent
    skills_dir = script_dir / "skills"
    version_file = script_dir / "VERSION"
    if skills_dir.is_dir() and version_file.is_file():
        return script_dir
    return None


def fetch_remote_skills(repo=DEFAULT_REPO, version_tag=None):
    """Download skills from GitHub. Returns (tmp_dir_path, source_root_path).

    Caller must clean up tmp_dir_path when done.
    """
    if version_tag:
        zip_url = f"https://github.com/{repo}/archive/refs/tags/{version_tag}.zip"
    else:
        zip_url = f"https://github.com/{repo}/archive/refs/heads/{DEFAULT_BRANCH}.zip"

    print(f"Fetching skills from {zip_url} ...")
    try:
        response = urlopen(zip_url, timeout=30)
        data = response.read()
    except URLError as e:
        print(f"Error: Failed to download from GitHub: {e}")
        print(f"  URL: {zip_url}")
        print("  Check your internet connection, or download the zip manually from:")
        print(f"  https://github.com/{repo}/releases")
        sys.exit(1)

    tmp_dir = Path(tempfile.mkdtemp(prefix="tdmcp-skills-"))
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            zf.extractall(tmp_dir)
    except zipfile.BadZipFile:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print("Error: Downloaded file is not a valid zip archive.")
        sys.exit(1)

    # GitHub zips contain a single root directory (e.g. TDMCPSkills-main/)
    children = [d for d in tmp_dir.iterdir() if d.is_dir()]
    if len(children) == 1:
        source_root = children[0]
    else:
        source_root = tmp_dir

    # Verify it has what we need
    if not (source_root / "skills").is_dir() or not (source_root / "VERSION").is_file():
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print("Error: Downloaded archive does not contain expected skills/ and VERSION.")
        sys.exit(1)

    return tmp_dir, source_root


# ---------------------------------------------------------------------------
# Source readers
# ---------------------------------------------------------------------------

def get_version(source_dir):
    """Read version from VERSION file in source_dir."""
    version_file = source_dir / "VERSION"
    if not version_file.exists():
        print(f"Error: VERSION file not found in {source_dir}")
        sys.exit(1)
    return version_file.read_text().strip()


def get_source_skills(source_dir):
    """Find all td-* skill directories in the source skills/ folder."""
    skills_dir = source_dir / "skills"
    if not skills_dir.exists():
        print(f"Error: skills/ directory not found in {source_dir}")
        sys.exit(1)
    return sorted(
        d for d in skills_dir.iterdir()
        if d.is_dir() and d.name.startswith(SKILL_PREFIX)
    )


# ---------------------------------------------------------------------------
# Target helpers
# ---------------------------------------------------------------------------

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


def write_manifest(target_dir, version, skill_names, source_label, repo_path=None):
    """Write manifest to target directory."""
    manifest = {
        "version": version,
        "installed": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": source_label,
        "skills": skill_names,
    }
    if repo_path:
        manifest["repo_path"] = str(repo_path)
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


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def install_from(source_dir, target_dir, source_label, repo_path=None):
    """Install skills from source_dir into target_dir."""
    version = get_version(source_dir)
    source_skills = get_source_skills(source_dir)
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
        if target_dir.exists():
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

    write_manifest(target_dir, version, skill_names, source_label, repo_path)

    print(f"Installed TDMCPSkills v{version}")
    print(f"  {len(skill_names)} skills -> {target_dir}")
    for name in skill_names:
        print(f"    {name}")


def do_install(target_dir, repo=DEFAULT_REPO, version_tag=None):
    """Install or upgrade skills — auto-detects local vs remote source."""
    local_source = detect_local_source()

    if local_source:
        print(f"Installing from local source: {local_source}")
        source_label = f"local:{local_source}"
        install_from(local_source, target_dir, source_label, repo_path=local_source)
    else:
        tmp_dir = None
        try:
            tmp_dir, source_dir = fetch_remote_skills(repo, version_tag)
            source_label = f"github:{repo}@{version_tag or DEFAULT_BRANCH}"
            install_from(source_dir, target_dir, source_label)
        finally:
            if tmp_dir:
                shutil.rmtree(tmp_dir, ignore_errors=True)


def do_uninstall(target_dir):
    """Uninstall skills from target directory."""
    manifest = read_manifest(target_dir)
    if not manifest:
        print(f"No TDMCPSkills installation found in {target_dir}")
        print("(no manifest file -- nothing to uninstall)")
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


def check_remote_version(repo=DEFAULT_REPO):
    """Fetch the latest VERSION from GitHub. Returns version string or None."""
    url = f"https://raw.githubusercontent.com/{repo}/{DEFAULT_BRANCH}/VERSION"
    try:
        response = urlopen(url, timeout=10)
        return response.read().decode().strip()
    except (URLError, OSError):
        return None


def do_status(target_dir, repo=DEFAULT_REPO):
    """Report install status and check for updates."""
    manifest = read_manifest(target_dir)
    if not manifest:
        print(f"No TDMCPSkills installation found in {target_dir}")
        return

    version = manifest.get("version", "unknown")
    installed = manifest.get("installed", "unknown")
    source = manifest.get("source", "unknown")
    repo_path = manifest.get("repo_path")
    skill_names = manifest.get("skills", [])

    # Check which are actually present
    present = [n for n in skill_names if (target_dir / n).is_dir()]
    missing = [n for n in skill_names if n not in present]

    print(f"TDMCPSkills v{version}")
    print(f"  Installed: {installed}")
    print(f"  Source:    {source}")
    if repo_path:
        print(f"  Repo:      {repo_path}")
    print(f"  Location:  {target_dir}")
    print(f"  Skills:    {len(present)}/{len(skill_names)} present")

    if missing:
        print(f"  Missing:   {', '.join(missing)}")

    # Check for updates
    remote_version = check_remote_version(repo)
    if remote_version and remote_version != version:
        print(f"  Update available: v{version} -> v{remote_version}")
        print("  Run 'python install.py install' to update")
    elif remote_version:
        print("  Up to date")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="TDMCPSkills installer for Claude Code",
        epilog="When run from the TDMCPSkills repo, installs from local files. "
               "Otherwise fetches the latest from GitHub automatically.",
    )
    parser.add_argument(
        "command",
        choices=["install", "uninstall", "status"],
        help="Action to perform",
    )
    parser.add_argument(
        "--project",
        metavar="PATH",
        help="Target a project's .claude/skills/ instead of global ~/.claude/skills/",
    )
    parser.add_argument(
        "--version",
        metavar="TAG",
        dest="version_tag",
        help="Install a specific release tag (e.g. v1.0.0). Remote mode only.",
    )
    parser.add_argument(
        "--repo",
        metavar="OWNER/REPO",
        default=DEFAULT_REPO,
        help=f"GitHub repository to fetch from (default: {DEFAULT_REPO})",
    )

    args = parser.parse_args()
    target_dir = resolve_target(args.project)

    if args.command == "install":
        do_install(target_dir, repo=args.repo, version_tag=args.version_tag)
    elif args.command == "uninstall":
        do_uninstall(target_dir)
    elif args.command == "status":
        do_status(target_dir, repo=args.repo)


if __name__ == "__main__":
    main()
