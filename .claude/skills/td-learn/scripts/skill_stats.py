#!/usr/bin/env python3
"""Report line and token counts for all skill files, CLAUDE.md, and SKILLS.md.

Scans both `skills/` (distributed) and `.claude/skills/` (contributor-only).
"""

import sys
from pathlib import Path

# Rough token estimate: ~4 chars per token for mixed English/code/markdown.
# Not exact, but close enough for budget tracking without external dependencies.
CHARS_PER_TOKEN = 4
LINE_BUDGET = 80
TOKEN_BUDGET = 4000


def estimate_tokens(text: str) -> int:
    return len(text) // CHARS_PER_TOKEN


def find_repo_root(start: Path) -> Path:
    """Walk up from `start` looking for VERSION + skills/ (repo root markers)."""
    for p in [start, *start.parents]:
        if (p / "VERSION").exists() and (p / "skills").is_dir():
            return p
    return start


def collect_skills(parent: Path, label_prefix: str = "") -> list:
    """Return [(label, path)] for every SKILL.md in a skills-dir layout."""
    out = []
    if not parent.exists():
        return out
    for skill_dir in sorted(parent.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            out.append((f"{label_prefix}{skill_dir.name}/SKILL.md", skill_file))
    return out


def main():
    root = find_repo_root(Path(__file__).resolve())

    files = []

    # Repo-level markdown
    for name in ("CLAUDE.md", "SKILLS.md"):
        path = root / name
        if path.exists():
            files.append((name, path))

    # Distributed skills (plugin + install.py)
    files.extend(collect_skills(root / "skills"))

    # Contributor-only skills (auto-load when working in this repo)
    files.extend(collect_skills(root / ".claude" / "skills", label_prefix=".claude/"))

    rows = []
    for label, path in files:
        text = path.read_text(encoding="utf-8")
        lines = text.count("\n")
        tokens = estimate_tokens(text)
        flags = []
        if "SKILL.md" in label:
            if lines > LINE_BUDGET:
                flags.append(f">{LINE_BUDGET}L")
            if tokens > TOKEN_BUDGET:
                flags.append(f">{TOKEN_BUDGET}T")
        rows.append((lines, tokens, label, " ".join(flags)))

    rows.sort(key=lambda r: r[1], reverse=True)

    print(f"{'Lines':>6}  {'Tokens':>6}  {'File':<45} {'Status'}")
    print(f"{'-'*6}  {'-'*6}  {'-'*45} {'-'*10}")
    for lines, tokens, label, flags in rows:
        status = flags if flags else "OK"
        print(f"{lines:>6}  {tokens:>6}  {label:<45} {status}")

    total_lines = sum(r[0] for r in rows)
    total_tokens = sum(r[1] for r in rows)
    print(f"{'-'*6}  {'-'*6}  {'-'*45}")
    print(f"{total_lines:>6}  {total_tokens:>6}  TOTAL")


if __name__ == "__main__":
    main()
