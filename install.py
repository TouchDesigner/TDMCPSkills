#!/usr/bin/env python3
"""TDMCPSkills installer — install, uninstall, or check status of TouchDesigner skills.

Supports multiple agent hosts through install targets:

    claude   ~/.claude/skills/                    (Claude Code)
    codex    ~/.codex/skills/                     (Codex; project scope is .agents/skills/)
    agy      ~/.gemini/antigravity-cli/skills/    (Antigravity; project scope is .agents/skills/)
    all      claude + codex + agy
    others   codex + agy  (everything except Claude Code)

Paths come from hosts.py, which records the CLI version each one was tested
against. Re-test and update that stamp rather than trusting a stale entry.

Dual-mode: when run from the TDMCPSkills repo (skills/ dir present), installs from
local files. When run standalone from any directory, fetches the latest from GitHub.

Usage:
    python install.py install --target claude       # Claude Code global install
    python install.py install --target codex --project .    # project-local
    python install.py status --target claude
    python install.py uninstall --target claude

Skill installation does NOT configure the TDMCP MCP server — see README.md for
per-host MCP configuration.
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
DEFAULT_TARGET = "claude"


# ---------------------------------------------------------------------------
# Target profiles
# ---------------------------------------------------------------------------
# One source of truth, shared with TDMCP's in-component installer: hosts.py.
# Adding support for a new agent means adding a Host there, not editing this
# file. `TARGETS` stays the local name because --target is the user-facing flag.

from hosts import HOSTS as TARGETS, ALL_HOSTS as ALL_TARGETS, PRESETS, expand_hosts, copy_hosts

expand_targets = expand_hosts


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
# Manifest helpers
# ---------------------------------------------------------------------------

def read_manifest(target_dir):
    """Read existing manifest from target, or None."""
    manifest_path = target_dir / MANIFEST_NAME
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def write_manifest(target_dir, target_ident, version, skill_names, source_label, repo_path=None):
    """Write manifest to target directory."""
    manifest = {
        "target": target_ident,
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


def find_unmanaged_conflicts(target_dir, incoming_names, manifest):
    """Skill dirs that would be overwritten but are not owned by our manifest."""
    if not target_dir.exists():
        return []
    owned = set(manifest.get("skills", [])) if manifest else set()
    conflicts = []
    for name in incoming_names:
        path = target_dir / name
        if path.is_dir() and name not in owned:
            conflicts.append(name)
    return conflicts


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def install_from(source_dir, target, target_dir, source_label, repo_path=None, replace=False):
    """Install skills from source_dir into target_dir."""
    version = get_version(source_dir)
    source_skills = get_source_skills(source_dir)
    skill_names = [d.name for d in source_skills]

    manifest = read_manifest(target_dir)

    # Never overwrite skill directories we don't own unless told to
    conflicts = find_unmanaged_conflicts(target_dir, skill_names, manifest)
    if conflicts and not replace:
        print(f"Error: {target_dir} contains skill directories not managed by TDMCPSkills:")
        for name in conflicts:
            print(f"    {name}")
        print("  These were not installed by this tool (or the manifest is missing).")
        print("  Re-run with --replace to overwrite them, or move them out of the way.")
        sys.exit(1)

    target_dir.mkdir(parents=True, exist_ok=True)

    # Remove the previous install — only what our manifest records
    if manifest:
        old_names = manifest.get("skills", [])
        old_version = manifest.get("version", "unknown")
        removed = remove_skills(target_dir, old_names)
        if removed:
            print(f"Removed {len(removed)} skills from previous install (v{old_version})")

    # Copy skills
    for source in source_skills:
        dest = target_dir / source.name
        if dest.exists():
            shutil.rmtree(dest)  # unmanaged conflict, user passed --replace
        shutil.copytree(source, dest)

    write_manifest(target_dir, target.ident, version, skill_names, source_label, repo_path)

    print(f"Installed TDMCPSkills v{version} [{target.ident}]")
    print(f"  {len(skill_names)} skills -> {target_dir}")
    for name in skill_names:
        print(f"    {name}")
    print(f"  {target.reload_hint}")


def do_install(target, target_dir, repo=DEFAULT_REPO, version_tag=None, replace=False):
    """Install or upgrade skills — auto-detects local vs remote source."""
    local_source = detect_local_source()

    if local_source:
        print(f"Installing from local source: {local_source}")
        source_label = f"local:{local_source}"
        install_from(local_source, target, target_dir, source_label,
                     repo_path=local_source, replace=replace)
    else:
        tmp_dir = None
        try:
            tmp_dir, source_dir = fetch_remote_skills(repo, version_tag)
            source_label = f"github:{repo}@{version_tag or DEFAULT_BRANCH}"
            install_from(source_dir, target, target_dir, source_label, replace=replace)
        finally:
            if tmp_dir:
                shutil.rmtree(tmp_dir, ignore_errors=True)


def do_uninstall(target, target_dir):
    """Uninstall skills from target directory — only manifest-owned skills."""
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

    print(f"Uninstalled TDMCPSkills v{version} [{target.ident}]")
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


def report_other_installs(current_target, project_path):
    """Note other known global installs so duplicate discovery is visible."""
    if project_path:
        return
    others = []
    for ident, target in TARGETS.items():
        if ident == current_target.ident or not target.copies_skills:
            continue
        if read_manifest(target.global_path):
            others.append(f"{ident} ({target.global_path})")
    if others:
        print("  Also installed at: " + "; ".join(others))
        print("  (multiple discovery locations can produce duplicate skills in some hosts —")
        print("   prefer one primary target per machine)")


def do_status(target, target_dir, project_path, repo=DEFAULT_REPO):
    """Report install status and check for updates."""
    manifest = read_manifest(target_dir)
    if not manifest:
        print(f"No TDMCPSkills installation found in {target_dir} [{target.ident}]")
        report_other_installs(target, project_path)
        return

    version = manifest.get("version", "unknown")
    installed = manifest.get("installed", "unknown")
    source = manifest.get("source", "unknown")
    repo_path = manifest.get("repo_path")
    skill_names = manifest.get("skills", [])

    # Check which are actually present
    present = [n for n in skill_names if (target_dir / n).is_dir()]
    missing = [n for n in skill_names if n not in present]

    print(f"TDMCPSkills v{version} [{target.ident}]")
    print(f"  Installed: {installed}")
    print(f"  Source:    {source}")
    if repo_path:
        print(f"  Repo:      {repo_path}")
    print(f"  Location:  {target_dir}")
    print(f"  Skills:    {len(present)}/{len(skill_names)} present")

    if missing:
        print(f"  Missing:   {', '.join(missing)}")

    report_other_installs(target, project_path)

    # Check for updates
    remote_version = check_remote_version(repo)
    if remote_version and remote_version != version:
        print(f"  Update available: v{version} -> v{remote_version}")
        print(f"  Run 'python install.py install --target {target.ident}' to update")
    elif remote_version:
        print("  Up to date")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="TDMCPSkills installer for agent CLIs (Claude Code, Codex, Gemini CLI, OpenCode)",
        epilog="When run from the TDMCPSkills repo, installs from local files. "
               "Otherwise fetches the latest from GitHub automatically. "
               "Installing skills does not configure the TDMCP MCP server — see README.md.",
    )
    parser.add_argument(
        "command",
        choices=["install", "uninstall", "status"],
        help="Action to perform",
    )
    parser.add_argument(
        "--target",
        choices=[*copy_hosts(), *sorted(PRESETS)],
        default=None,
        help=f"Install target: one of the hosts in hosts.py, or 'all' for the "
             f"verified default set. Default: {DEFAULT_TARGET}",
    )
    parser.add_argument(
        "--project",
        metavar="PATH",
        help="Target a project's skills directory (e.g. .agents/skills/ or .claude/skills/) "
             "instead of the global location",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Overwrite conflicting td-* skill directories not managed by TDMCPSkills",
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

    target_name = args.target
    if target_name is None:
        target_name = DEFAULT_TARGET
        print(f"No --target given; defaulting to '{DEFAULT_TARGET}'.\n")

    # Codex and Antigravity share <project>/.agents/skills, so `--target all
    # --project X` would otherwise install the same skills there twice and write
    # the manifest twice over.
    done_dirs = {}
    for target in expand_targets(target_name):
        try:
            target_dir = target.resolve(args.project)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        if target_dir in done_dirs:
            print(f"Skipping {target.ident}: same directory as "
                  f"{done_dirs[target_dir]} ({target_dir})\n")
            continue
        done_dirs[target_dir] = target.ident
        if args.command == "install":
            do_install(target, target_dir, repo=args.repo,
                       version_tag=args.version_tag, replace=args.replace)
        elif args.command == "uninstall":
            do_uninstall(target, target_dir)
        elif args.command == "status":
            do_status(target, target_dir, args.project, repo=args.repo)
        print()


if __name__ == "__main__":
    main()
