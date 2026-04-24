# TDMCPSkills

TouchDesigner skills for Claude Code. Teaches Claude how to build TouchDesigner networks effectively using the [TDMCP](https://github.com/TouchDesigner/TDMCP) server.

17 skills cover TOPs, CHOPs, POPs, SOPs, GLSL, materials, components, UI, and end-to-end workflow. See [SKILLS.md](SKILLS.md) for the full list.

## Requirements

- [Claude Code](https://claude.ai/code) (CLI or Desktop App)
- [TDMCP](https://github.com/TouchDesigner/TDMCP) installed and running in TouchDesigner
- Python 3.7+ (only for the script install path)

## Install — Claude Code plugin (recommended)

In Claude Code:

```
/plugin marketplace add TouchDesigner/TDMCPSkills
/plugin install tdmcp-skills@touchdesigner
```

This installs the 17 distributed skills and auto-registers the TDMCP MCP connection at `http://localhost:13316/mcp`. Start TDMCP inside TouchDesigner before using — Claude Code retries automatically until the server responds.

Update when a new version is published:

```
/plugin marketplace update touchdesigner
```

Uninstall:

```
/plugin uninstall tdmcp-skills
```

## Install — script (alternative)

For environments without plugin support, CI, or users who prefer a script:

```bash
git clone https://github.com/TouchDesigner/TDMCPSkills.git
cd TDMCPSkills
python install.py install
```

Installs skills to `~/.claude/skills/` (available in every project). The script does **not** register the MCP server — configure it yourself in `~/.claude.json` or a project `.mcp.json`:

```json
{
  "mcpServers": {
    "tdmcp": {
      "type": "http",
      "url": "http://localhost:13316/mcp"
    }
  }
}
```

Other install modes:

```bash
# Install into a specific project (overrides the global set for that project)
python install.py install --project /path/to/td-project

# Check install status and available updates
python install.py status

# Update from a fresh pull
git pull && python install.py install

# Uninstall
python install.py uninstall
python install.py uninstall --project .
```

If no local repo is detected, `install.py install` fetches the latest from GitHub directly — works from an extracted release zip too.

## For Contributors

### Fork workflow

Fork the repo, work on a branch:

```bash
git clone https://github.com/YOUR_USERNAME/TDMCPSkills.git
cd TDMCPSkills
git checkout -b my-custom-skills
```

Edit any skill under `skills/`, then pick a testing loop:

**Via the script** — reinstalls globally, available in every project:

```bash
python install.py install
```

**Via the plugin** — install this working tree as a local marketplace (fastest iteration; no push needed):

```
/plugin marketplace add "/absolute/path/to/TDMCPSkills"
/plugin install tdmcp-skills@touchdesigner
```

After edits, pick up changes with:

```
/plugin marketplace update touchdesigner
```

Stay current with upstream:

```bash
git fetch upstream
git merge upstream/main
```

### Contributor skills (`/td-learn`)

Contributor-only skills live in this repo's `.claude/skills/` and auto-load only when Claude Code is working inside a clone of TDMCPSkills. They are **not** distributed via the plugin or `install.py`.

**`/td-learn`** — review a build session and propose skill improvements:

- Flags struggles, stalls, and wrong outcomes from the conversation
- Audits loaded skills for missing knowledge, contradictions, redundancy
- Runs a size/token audit across all skills
- Proposes specific edits to skill files

Run after each build session, commit the proposed improvements on your branch, and reinstall to validate.

**`/td-skills-local`** — legacy helper for installing skills into a specific project's `.claude/skills/`. Mostly superseded by the plugin install path.

## Contributors

- Jarrett Smith (Derivative)
- Tim Gerritsen (y=f(x) Lab)
