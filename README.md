# TDMCPSkills

Portable Agent Skills for TouchDesigner. Teaches AI coding agents how to build TouchDesigner networks effectively using the [TDMCP](https://github.com/TouchDesigner/TDMCP) server.

18 skills cover TOPs, CHOPs, POPs, SOPs, GLSL, materials, components, UI, and end-to-end workflow. See [SKILLS.md](SKILLS.md) for the full list.

> **The `td-` prefix is reserved.** Installing skills — via the in-TD component, the plugin, or `install.py` — **manages the entire `td-` namespace** in the target skill directory: any `td-*` skill the current release no longer ships is removed on update. Author your own skills under your **own prefix** (e.g. `mystudio-foo`); anything named `td-*` is owned by this system and may be replaced or deleted without warning.

Three separate pieces work together:

- **Skills** — reusable TouchDesigner workflow instructions (this repo)
- **MCP** — the live TDMCP connection to TouchDesigner (configured per host, see below)
- **Plugins/extensions** — provider-specific packaging (currently Claude Code only)

## Supported hosts

| Host | Skills location | MCP config |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` or plugin | `.mcp.json` / `~/.claude.json` (plugin auto-registers) |
| Codex | `~/.agents/skills/` (or `~/.codex/skills/`) | `~/.codex/config.toml` |
| Gemini CLI | `~/.agents/skills/` / `.agents/skills/` | `.gemini/settings.json` |
| OpenCode | `~/.agents/skills/` / `.agents/skills/` | `opencode.json` |

## Requirements

- One of the supported agent CLIs above
- [TDMCP](https://github.com/TouchDesigner/TDMCP) installed and running in TouchDesigner
- Python 3.7+ (only for the script install path)

## Quick install — portable (Codex, Gemini CLI, OpenCode)

```bash
git clone https://github.com/TouchDesigner/TDMCPSkills.git
cd TDMCPSkills
python install.py install --target agents
```

Installs skills to `~/.agents/skills/`, the shared discovery location for portable Agent Skills. Project-local instead:

```bash
python install.py install --target agents --project /path/to/your/project
```

Installing skills does **not** configure the MCP connection — do that once per host (next section).

## TDMCP MCP configuration

TDMCP serves MCP over HTTP at `http://localhost:13316/mcp`. Start it inside TouchDesigner before using any agent.

**Claude Code** — project `.mcp.json` (or `~/.claude.json`):

```json
{
  "mcpServers": {
    "tdmcp": { "type": "http", "url": "http://localhost:13316/mcp" }
  }
}
```

**Codex** — `~/.codex/config.toml`:

```toml
[mcp_servers.touchdesigner]
url = "http://localhost:13316/mcp"
```

**Gemini CLI** — project `.gemini/settings.json` (or `~/.gemini/settings.json`):

```json
{
  "mcpServers": {
    "tdmcp": { "httpUrl": "http://localhost:13316/mcp" }
  }
}
```

**OpenCode** — project `opencode.json` (or `~/.config/opencode/opencode.json`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "tdmcp": { "type": "remote", "url": "http://localhost:13316/mcp", "enabled": true }
  }
}
```

## Install — Claude Code plugin (recommended for Claude Code)

In Claude Code:

```
/plugin marketplace add TouchDesigner/TDMCPSkills
/plugin install tdmcp-skills@touchdesigner
```

This installs the 18 distributed skills and auto-registers the TDMCP MCP connection. Update with `/plugin marketplace update touchdesigner`; uninstall with `/plugin uninstall tdmcp-skills`.

Script alternative for Claude Code:

```bash
python install.py install --target claude
```

## Install targets

```bash
python install.py install --target agents        # ~/.agents/skills/  (Codex, Gemini CLI, OpenCode)
python install.py install --target claude        # ~/.claude/skills/  (Claude Code)
python install.py install --target codex-legacy  # ~/.codex/skills/   (Codex compatibility, global only)
python install.py install --target all           # agents + claude

python install.py status --target agents         # install status + update check
python install.py uninstall --target agents
```

Notes:

- Each target keeps its own manifest; install/status/uninstall never touch another target.
- The installer only ever removes skill directories recorded in its own manifest. Conflicting `td-*` directories it doesn't own stop the install with an error (override with `--replace`).
- Pick **one primary target per host** — installing the same skills in multiple discovery locations can produce duplicates. `status` reports other known installs.
- Running `install.py` with no `--target` currently defaults to `claude` for backward compatibility; this default will move to `agents` in a future release.
- If no local repo is detected, `install.py install` fetches the latest from GitHub directly.

### Migrating an existing `~/.claude/skills` install

Nothing breaks: `--target claude` preserves the previous behavior exactly. To also use another host, additionally run `python install.py install --target agents`. The two installs are independent.

## Validation

```bash
python validate.py
```

Checks every distributed skill against the portable contract: frontmatter (`name` + `description`), name/directory match, naming rules, resolvable references, and no provider-specific commands or paths in shared content.

## For Contributors

### Fork workflow

Fork the repo, work on a branch:

```bash
git clone https://github.com/YOUR_USERNAME/TDMCPSkills.git
cd TDMCPSkills
git checkout -b my-custom-skills
```

Edit any skill under `skills/`, run `python validate.py`, then pick a testing loop:

**Via the script** — reinstalls globally, available in every project:

```bash
python install.py install --target agents   # or --target claude
```

**Via the plugin (Claude Code)** — install this working tree as a local marketplace (fastest iteration; no push needed):

```
/plugin marketplace add "/absolute/path/to/TDMCPSkills"
/plugin install tdmcp-skills@touchdesigner
```

After edits, pick up changes with `/plugin marketplace update touchdesigner`.

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

## Compatibility notes

- Shared skill content is provider-neutral: MCP tool names are unqualified (`get_help`, not a host-prefixed name) because each host namespaces tools differently.
- Skill discovery and activation behavior varies by host; if a host doesn't auto-activate a skill, ask the agent to read the relevant `SKILL.md` explicitly.
- Smaller/local models (tested: qwen3:14b via OpenCode + Ollama) discover and load skills but tend to skip the cross-cutting `td-general` skill and jump straight to a builder skill, losing naming and get-help-first conventions. Mitigate by instructing "load `td-general` first" explicitly in the project's agent instructions (`AGENTS.md`).
- LM Studio is out of scope.

## Contributors

- Jarrett Smith (Derivative)
- Tim Gerritsen (y=f(x) Lab)
