# TDMCPSkills

TouchDesigner skills for Claude Code. Teaches Claude how to build TouchDesigner networks effectively using the [TDMCP](https://github.com/TouchDesigner/TDMCP) server.

## Install (from git clone)

Clone the repo and install globally:

```bash
git clone https://github.com/TouchDesigner/TDMCPSkills.git
cd TDMCPSkills
python install.py install
```

This installs skills to `~/.claude/skills/` (available in all projects) and registers the repo path so you can install skills into projects from Claude Code.

## Install (from release zip)

Download the latest release zip, extract it, and run:

```bash
python install.py install
```

When no local repo is detected, the installer can also fetch directly from GitHub:

```bash
python install.py install
```

## Project-Local Skills

Once installed globally from a git clone, you can install skills into any project directly from Claude Code:

1. Open Claude Code in your project directory
2. Ask Claude to `/td-skills-local` or say "install skills locally"
3. Claude reads the registered repo path and installs skills into `./.claude/skills/`

Project-level skills override global skills of the same name. This lets you customize skills per-project while keeping global defaults.

You can also do it manually:

```bash
python install.py install --project /path/to/your/td-project
```

## Update

From the repo:

```bash
git pull
python install.py install
```

Or from a fresh release zip, run the same install command. The installer replaces the previous version cleanly.

## Uninstall

```bash
python install.py uninstall
```

Or for a project-local install:

```bash
python install.py uninstall --project /path/to/your/td-project
```

## Check Status

```bash
python install.py status
python install.py status --project /path/to/your/td-project
```

Shows installed version, source, skill count, and checks for available updates.

## Requirements

- Python 3.7+
- [Claude Code](https://claude.ai/code) (CLI or Desktop App)
- [TDMCP](https://github.com/TouchDesigner/TDMCP) server running in TouchDesigner

## Skills Included

See [SKILLS.md](SKILLS.md) for the full list of 18 skills covering TOPs, CHOPs, POPs, SOPs, GLSL, materials, components, UI, and workflow.
