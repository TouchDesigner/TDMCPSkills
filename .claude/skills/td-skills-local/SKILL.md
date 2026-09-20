---
description: Install, update, or remove TD skills in the current project. Use when the user asks to install skills locally, update local skills, or remove local skill overrides.
user_invocable: true
---

# td-skills-local

Manages project-local TD skill installations. Project-level skills in `.claude/skills/` override global skills in `~/.claude/skills/` when names match.

Installation lives in the **TDMCP component**, not in this repo. This repo is skills content only — there is no `install.py` here any more.

## Prerequisites

- TouchDesigner is running with the TDMCP component active
- You can reach it through the `touchdesigner` MCP server (try `project_info`)

If TouchDesigner is not running, say so and stop. Copying skill folders by hand works but leaves no manifest, so the component can neither update nor uninstall them afterwards — it only manages what it recorded installing.

## Process

### 1. Find the component

`project_info` gives the project. The component is normally `/TDMCP`; confirm with `list_operators` if it is not.

### 2. Set the target, then act

`Installfor` and `Installscope` live on the **MCP** page, `Skillssource` on the **Skills** page. Set them with `set_parameters`, then pulse:

| Parameter | Value |
| --- | --- |
| `Installfor` | the agent, one at a time: `claude`, `codex`, `agy`, `cursor`, `opencode` |
| `Installscope` | `project` for project-local, `user` for global. The menu is rebuilt per agent, so only supported scopes appear |
| `Skillssource` | path to a TDMCPSkills checkout, or blank to fetch the published release |

Then:

- **Install / update**: pulse `Installagentskills`
- **Uninstall / remove**: pulse `Uninstallagentskills`. `Skillsscope` decides how wide: `current` follows the MCP page, `project` / `user` sweep every agent at that scope, `everywhere` clears all of them
- **Status / check**: read `Agentskillsstatus`

Pulses are handled on the next cook, so read the status back in a **separate** call — reading it in the same call returns the previous value.

### 3. Confirm before acting

Say which host, which scope and which source you are about to use, and that `local` writes into the current project. Then execute.

### 4. Report results

Read `Agentskillsstatus` and relay it. It reports per host and scope, names skills the manifest lists but that are missing from disk, and flags an install that is behind its source. The resolved directories are in that parameter's tooltip (`par.help`) when you need exact paths.

## Notes

- Project skills override global skills of the same name — this is built into Claude Code
- To customize one skill for a project, install locally then edit `.claude/skills/td-<name>/SKILL.md`
- To revert to global skills, uninstall the local copy
- Codex and Antigravity share `<project>/.agents/skills/`, so installing for either at project scope serves both
- The installer prunes only skills its own manifest recorded; a `td-*` folder it did not install is left alone
- `Skillsoverview` on the Skills page lists every destination currently holding skills — read it before any wide uninstall
