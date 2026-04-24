---
description: Install, update, or remove TDMCPSkills in the current project. Use when the user asks to install skills locally, update local skills, or remove local skill overrides.
user_invocable: true
---

# td-skills-local

Manages project-local TD skill installations. Project-level skills in `.claude/skills/` override global skills in `~/.claude/skills/` when names match.

## Prerequisites

- TDMCPSkills must be installed globally first (`python install.py install` from the skills repo)
- The global install must have been done from a local git repo (not a zip), so `repo_path` is in the manifest

## Process

### 1. Read the global manifest

Read `~/.claude/skills/td-skills-manifest.json`. Extract the `repo_path` field.

If `repo_path` is missing or the path doesn't exist, tell the user:
- "No skills repo registered. Run `python install.py install` from your local TDMCPSkills repo first."

### 2. Determine the action

Based on what the user asked:

- **Install / update**: run `python <repo_path>/install.py install --project .`
- **Uninstall / remove**: run `python <repo_path>/install.py uninstall --project .`
- **Status / check**: run `python <repo_path>/install.py status --project .`

### 3. Confirm before acting

Tell the user what you're about to do and which repo path you're using. Then execute.

### 4. Report results

Show the output from install.py. If installing, note that project-level skills now override global ones.

## Notes

- Project skills override global skills of the same name — this is built into Claude Code
- To customize a specific skill for a project, install locally then edit the project's `.claude/skills/td-<name>/SKILL.md`
- To revert to global skills, uninstall the local copy
