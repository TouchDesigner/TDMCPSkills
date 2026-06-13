#!/usr/bin/env python3
"""Validate distributed TDMCPSkills against the portable Agent Skills contract.

Checks every skills/td-*/ directory:
- SKILL.md exists with valid YAML-style frontmatter
- frontmatter has exactly the portable fields: name, description
- name matches the containing directory
- name uses lowercase letters, digits, and hyphens only (max 64 chars)
- description is non-empty and within host limits (max 1024 chars)
- relative links and referenced files (reference.md, examples.md, scripts) resolve
- no provider-only commands or paths leak into distributed content

Runs without installing anything. Exit code 0 = all skills valid.

Usage:
    python validate.py
"""

import json
import re
import sys
from pathlib import Path

SKILL_PREFIX = "td-"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
NAME_MAX = 64
DESCRIPTION_MAX = 1024

# Provider-specific terms that must not appear in distributed skill content.
# Each entry: (compiled pattern, human-readable reason)
PROVIDER_PATTERNS = [
    (re.compile(r"\bClaude\b"), "references Claude — use 'agent' or 'host'"),
    (re.compile(r"/td-learn\b"), "references contributor-only /td-learn command"),
    (re.compile(r"\.claude/"), "references Claude-specific path"),
    (re.compile(r"\.codex/"), "references Codex-specific path"),
    (re.compile(r"\.gemini/"), "references Gemini-specific path"),
    (re.compile(r"mcp__\w+__"), "uses host-qualified MCP tool name — keep tool names unqualified"),
]

# Markdown link target pattern: [text](target)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#\s]+)[^)]*\)")


def parse_frontmatter(text, errors, label):
    """Parse simple key: value frontmatter. Returns dict or None."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        errors.append(f"{label}: missing frontmatter opening '---' on line 1")
        return None
    fields = {}
    for i, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return fields
        if not line.strip():
            continue
        if line.startswith((" ", "\t")):
            errors.append(f"{label}: line {i}: nested/indented frontmatter not allowed for portable skills")
            return None
        if ":" not in line:
            errors.append(f"{label}: line {i}: invalid frontmatter line {line!r}")
            return None
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip("'\"")
    errors.append(f"{label}: frontmatter never closed with '---'")
    return None


def validate_skill(skill_dir, errors):
    label = f"skills/{skill_dir.name}"
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"{label}: missing SKILL.md")
        return

    text = skill_md.read_text(encoding="utf-8")
    fields = parse_frontmatter(text, errors, f"{label}/SKILL.md")
    if fields is None:
        return

    # Required portable fields
    name = fields.get("name")
    description = fields.get("description")
    if not name:
        errors.append(f"{label}/SKILL.md: frontmatter missing 'name'")
    else:
        if name != skill_dir.name:
            errors.append(f"{label}/SKILL.md: name {name!r} does not match directory {skill_dir.name!r}")
        if not NAME_RE.match(name):
            errors.append(f"{label}/SKILL.md: name {name!r} must be lowercase letters, digits, hyphens")
        if len(name) > NAME_MAX:
            errors.append(f"{label}/SKILL.md: name exceeds {NAME_MAX} chars")
    if not description:
        errors.append(f"{label}/SKILL.md: frontmatter missing or empty 'description'")
    elif len(description) > DESCRIPTION_MAX:
        errors.append(f"{label}/SKILL.md: description exceeds {DESCRIPTION_MAX} chars ({len(description)})")

    extra = set(fields) - {"name", "description"}
    if extra:
        errors.append(f"{label}/SKILL.md: non-portable frontmatter fields: {', '.join(sorted(extra))}")

    # Provider-only content in every markdown/script file in the skill
    for f in sorted(skill_dir.rglob("*")):
        if not f.is_file() or f.suffix not in {".md", ".py", ".txt"}:
            continue
        rel = f.relative_to(skill_dir.parent.parent)
        content = f.read_text(encoding="utf-8")
        for lineno, line in enumerate(content.split("\n"), start=1):
            for pattern, reason in PROVIDER_PATTERNS:
                if pattern.search(line):
                    errors.append(f"{rel}:{lineno}: {reason}")

    # Relative links from SKILL.md must resolve
    for target in LINK_RE.findall(text):
        if re.match(r"^[a-z]+://", target) or target.startswith("/"):
            continue
        if not (skill_dir / target).exists():
            errors.append(f"{label}/SKILL.md: relative link target does not exist: {target}")

    # Referenced companion files mentioned in backticks must exist
    for companion in re.findall(r"`(reference\.md|examples\.md|scripts/[\w./-]+)`", text):
        if not (skill_dir / companion).exists():
            errors.append(f"{label}/SKILL.md: references `{companion}` which does not exist")


def validate_version_sync(repo, errors):
    """VERSION is canonical; both Claude plugin fields must match it exactly."""
    version_file = repo / "VERSION"
    if not version_file.is_file():
        errors.append("VERSION: file missing")
        return
    version = version_file.read_text(encoding="utf-8").strip()
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        errors.append(f"VERSION: {version!r} is not plain semver (X.Y.Z)")

    for rel, extract in [
        (".claude-plugin/plugin.json", lambda d: d.get("version")),
        (".claude-plugin/marketplace.json", lambda d: (d.get("plugins") or [{}])[0].get("version")),
    ]:
        path = repo / rel
        if not path.is_file():
            errors.append(f"{rel}: file missing")
            continue
        try:
            found = extract(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError as e:
            errors.append(f"{rel}: invalid JSON ({e})")
            continue
        if found != version:
            errors.append(f"{rel}: version {found!r} does not match VERSION {version!r}")


def main():
    repo = Path(__file__).resolve().parent
    skills_root = repo / "skills"
    if not skills_root.is_dir():
        print("Error: skills/ directory not found — run from the TDMCPSkills repo")
        return 1

    skill_dirs = sorted(
        d for d in skills_root.iterdir()
        if d.is_dir() and d.name.startswith(SKILL_PREFIX)
    )
    if not skill_dirs:
        print("Error: no td-* skill directories found in skills/")
        return 1

    errors = []
    validate_version_sync(repo, errors)
    for skill_dir in skill_dirs:
        validate_skill(skill_dir, errors)

    # Non-prefixed directories are not distributed — flag them.
    # Hidden/dot dirs (.claude, .git, tool/OS artifacts) are not skill attempts — ignore them.
    strays = [
        d.name for d in skills_root.iterdir()
        if d.is_dir() and not d.name.startswith(SKILL_PREFIX) and not d.name.startswith(".")
    ]
    for stray in strays:
        errors.append(f"skills/{stray}: directory lacks required '{SKILL_PREFIX}' prefix")

    if errors:
        print(f"FAIL — {len(errors)} problem(s) across {len(skill_dirs)} skills:\n")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"OK — {len(skill_dirs)} skills valid")
    for d in skill_dirs:
        print(f"  {d.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
