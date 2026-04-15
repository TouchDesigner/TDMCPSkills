#!/usr/bin/env python3
"""Report line and token counts for all skill files, CLAUDE.md, and SKILLS.md."""

import sys
from pathlib import Path

# Rough token estimate: ~4 chars per token for mixed English/code/markdown.
# Not exact, but close enough for budget tracking without external dependencies.
CHARS_PER_TOKEN = 4
LINE_BUDGET = 80
TOKEN_BUDGET = 4000


def estimate_tokens(text: str) -> int:
    return len(text) // CHARS_PER_TOKEN


def main():
    root = Path(__file__).resolve().parents[3]  # scripts -> learn -> skills -> repo root
    skills_dir = root / "skills"

    files = []

    # CLAUDE.md
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        files.append(("CLAUDE.md", claude_md))

    # SKILLS.md
    skills_md = skills_dir / "SKILLS.md"
    if skills_md.exists():
        files.append(("SKILLS.md", skills_md))

    # All SKILL.md files
    for skill_dir in sorted(skills_dir.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            files.append((f"{skill_dir.name}/SKILL.md", skill_file))

    # Collect stats
    rows = []
    for label, path in files:
        text = path.read_text(encoding="utf-8")
        lines = text.count("\n")
        tokens = estimate_tokens(text)
        flags = []
        if "SKILL.md" in label and label not in ("SKILLS.md",):
            if lines > LINE_BUDGET:
                flags.append(f">{LINE_BUDGET}L")
            if tokens > TOKEN_BUDGET:
                flags.append(f">{TOKEN_BUDGET}T")
        rows.append((lines, tokens, label, " ".join(flags)))

    # Sort by tokens descending
    rows.sort(key=lambda r: r[1], reverse=True)

    # Print
    print(f"{'Lines':>6}  {'Tokens':>6}  {'File':<40} {'Status'}")
    print(f"{'-'*6}  {'-'*6}  {'-'*40} {'-'*10}")
    for lines, tokens, label, flags in rows:
        status = flags if flags else "OK"
        print(f"{lines:>6}  {tokens:>6}  {label:<40} {status}")

    # Totals
    total_lines = sum(r[0] for r in rows)
    total_tokens = sum(r[1] for r in rows)
    print(f"{'-'*6}  {'-'*6}  {'-'*40}")
    print(f"{total_lines:>6}  {total_tokens:>6}  TOTAL")


if __name__ == "__main__":
    main()
