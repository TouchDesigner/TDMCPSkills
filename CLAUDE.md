# TDMCPSkills

Skills for the TouchDesigner MCP server. Each skill teaches Claude how to work with a specific TouchDesigner domain.

## Structure

- `skills/` — skill directories, each with `SKILL.md` + optional `reference.md`, `examples.md`
- `hooks/` — Claude Code hooks (tool-logger for session analytics)
- `SKILLS.md` — master index of all skills

## Developing Skills

1. Create a directory under `skills/` with at least a `SKILL.md`
2. Add `reference.md` and/or `examples.md` if the skill has enough material
3. Use YAML frontmatter with `description` and `user_invocable` fields in `SKILL.md`
4. Update `SKILLS.md` index
5. To deploy skills to a project, copy the skill directories into that project's `.claude/skills/`

## Learn Workflow

After build sessions, run `/learn` to analyze tool usage patterns:
- `python skills/learn/scripts/analyzer.py` — session log analysis
- `python skills/learn/scripts/skill_stats.py` — skill size/token audit

## Guidelines

- Keep skills under ~80 lines / ~4,000 tokens
- Terse bullets, no prose — state the rule, not the rationale
- One concept per line
- No tables — use bullet lists
- Procedures over declarations — teach *how to approach*, not *what to produce*
