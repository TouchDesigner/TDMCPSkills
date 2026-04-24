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

When no local repo is detected, the installer can also fetch directly from GitHub.

## Project-Local Install

Install skills into a specific project's `.claude/skills/` (overrides the global set for that project):

```bash
python install.py install --project /path/to/your/td-project
```

Remove them and revert to global:

```bash
python install.py uninstall --project .
```

## Customizing Skills (fork workflow)

You can fork the repo and create your own branch to customize skills for your workflow:

```bash
git clone https://github.com/YOUR_USERNAME/TDMCPSkills.git
cd TDMCPSkills
git checkout -b my-custom-skills
```

Edit any skill under `skills/`, then install globally:

```bash
python install.py install
```

To stay up to date with the standard skills while keeping your customizations:

```bash
git fetch upstream
git merge upstream/main
python install.py install
```

Reinstall after edits to push changes to any project using them.

## Improving Skills with `/td-learn` (Contributors)

`/td-learn` is a contributor tool that lives in this repo's `.claude/skills/` — it auto-loads only when Claude Code is working inside a clone of TDMCPSkills. End-user installs (plugin or `install.py`) don't include it.

Run `/td-learn` after a build session to:

- Review the conversation for struggles, stalls, and wrong outcomes
- Audit loaded skills for missing knowledge, contradictions, or redundancy
- Run a size/token audit across all skills to flag bloat
- Propose specific edits to skill files

Commit proposed improvements on your branch and reinstall.

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
python install.py uninstall --project .
```

## Check Status

```bash
python install.py status
python install.py status --project .
```

Shows installed version, source, skill count, and checks for available updates.

## Requirements

- Python 3.7+
- [Claude Code](https://claude.ai/code) (CLI or Desktop App)
- [TDMCP](https://github.com/TouchDesigner/TDMCP) server running in TouchDesigner

## Contributors

- Jarrett Smith (Derivative)
- Tim Gerritsen (y=f(x) Lab)

## Skills Included

See [SKILLS.md](SKILLS.md) for the full list of 18 skills covering TOPs, CHOPs, POPs, SOPs, GLSL, materials, components, UI, and workflow.
