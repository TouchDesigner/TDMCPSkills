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

## Project-Local Skills (`/td-skills-local`)

Once installed globally from a git clone, you can install skills into any project directly from Claude Code:

1. Open Claude Code in your project directory
2. Ask Claude to `/td-skills-local` or say "install skills locally"
3. Claude reads the registered repo path and installs skills into `./.claude/skills/`

Project-level skills override global skills of the same name. This lets you customize skills per-project while keeping global defaults.

You can also do it manually:

```bash
python install.py install --project /path/to/your/td-project
```

To remove local skills and revert to the global set:

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

Use `/td-skills-local` to push your updated skills into individual projects as you go.

## Improving Skills with `/td-learn`

The `td-learn` skill helps you improve the skill system based on real usage. After a build session, run `/td-learn` in Claude Code. It will:

- Analyze tool usage patterns from the session (which tools were called, how often, in what order)
- Flag inefficiencies like repeated calls, high-token responses, or `execute_code` where dedicated tools exist
- Audit loaded skills for missing knowledge, contradictions, or redundancy
- Propose specific edits to skill files

This is how you create and refine your own skills. If you notice Claude struggling with a particular pattern, `/td-learn` identifies the gap and suggests what to add. Commit your improvements to your branch and reinstall.

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

## Skills Included

See [SKILLS.md](SKILLS.md) for the full list of 18 skills covering TOPs, CHOPs, POPs, SOPs, GLSL, materials, components, UI, and workflow.
