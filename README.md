# TDMCPSkills

TouchDesigner skills for Claude Code. Teaches Claude how to build TouchDesigner networks effectively using the [TDMCP](https://github.com/TouchDesigner/TDMCP) server.

## Install

Download the latest release zip, extract it, and run:

```bash
python install.py install
```

This installs skills globally (`~/.claude/skills/`) so they're available in all your projects.

To install into a specific project instead:

```bash
python install.py install --project /path/to/your/td-project
```

## Update

Download the new release zip, extract it, and run the same install command. The installer replaces the previous version cleanly.

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

## Requirements

- Python 3.7+
- [Claude Code](https://claude.ai/code) (CLI or Desktop App)
- [TDMCP](https://github.com/TouchDesigner/TDMCP) server running in TouchDesigner

## Skills Included

See [SKILLS.md](SKILLS.md) for the full list of 17 skills covering TOPs, CHOPs, POPs, SOPs, GLSL, materials, components, UI, and workflow.
