# TDMCPSkills

Skills for the TouchDesigner MCP server. Each skill teaches Claude how to work with a specific TouchDesigner domain.

## Structure

- `skills/` — skill directories (all prefixed `td-`), each with `SKILL.md` + optional `reference.md`, `examples.md`
- `hooks/` — Claude Code hooks (tool-logger for session analytics)
- `install.py` — cross-platform installer (install, uninstall, status)
- `SKILLS.md` — master index of all skills

## Developing Skills

1. Create a directory under `skills/` with `td-` prefix and at least a `SKILL.md`
2. Add `reference.md` and/or `examples.md` if the skill has enough material
3. Use YAML frontmatter with `description` and `user_invocable` fields in `SKILL.md`
4. Update `SKILLS.md` index
5. To test: `python install.py install --project <td-project-path>`

## Learn Workflow

After build sessions, run `/td-learn` to analyze tool usage patterns:
- `python skills/td-learn/scripts/analyzer.py` — session log analysis
- `python skills/td-learn/scripts/skill_stats.py` — skill size/token audit

## Guidelines

- Keep skills under ~80 lines / ~4,000 tokens
- Terse bullets, no prose — state the rule, not the rationale
- One concept per line
- No tables — use bullet lists
- Procedures over declarations — teach *how to approach*, not *what to produce*
- All skill directories must use `td-` prefix for namespace isolation
