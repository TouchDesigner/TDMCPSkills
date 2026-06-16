# TDMCPSkills

Skills for the TouchDesigner MCP server. Each skill teaches Claude how to work with a specific TouchDesigner domain.

## Structure

- `skills/` — skill directories (all prefixed `td-`), each with `SKILL.md` + optional `reference.md`, `examples.md`
- `install.py` — cross-platform installer (install, uninstall, status)
- `SKILLS.md` — master index of all skills

## Workflow

1. **Scout** — `project_info`, find the right comp/path
2. **Plan** — load `td-build-planning` skill, decide operators, positions, builder skills
3. **Build** — execute using builder skills (td-top-family, td-chop-family, td-glsl-shaders, etc.)
4. **Review** — load `td-review-network` skill, check errors, verify wiring
5. **Cleanup** — always run `td-network-cleanup` skill after builds, align layout, annotate

## Guidelines

- Keep skills under ~80 lines / ~4,000 tokens
- Terse bullets, no prose — state the rule, not the rationale
- One concept per line
- No tables — use bullet lists
- Procedures over declarations — teach *how to approach*, not *what to produce*
- All skill directories must use `td-` prefix for namespace isolation

## Changelog

- Every change to distributed content (skills, `install.py`, `validate.py`, docs, `VERSION`) → add an entry under `[Unreleased]` in `CHANGELOG.md` before committing. Keep a Changelog format: Added / Changed / Fixed / Removed.
- Adding/removing a skill → also update its row in `td-general`'s Skill Map (`validate.py` enforces map↔skills sync).
