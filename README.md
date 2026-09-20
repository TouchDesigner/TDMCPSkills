# TDMCPSkills

Portable Agent Skills for TouchDesigner. Teaches AI coding agents how to build TouchDesigner networks effectively using the [TDMCP](https://github.com/TouchDesigner/TDMCP) server.

19 skills cover TOPs, CHOPs, POPs, SOPs, GLSL, materials, components, UI, and end-to-end workflow. See [SKILLS.md](SKILLS.md) for the full list.

> **The `td-` prefix is reserved.** Installing skills — via the in-TD component, the plugin, or `install.py` — **manages the entire `td-` namespace** in the target skill directory: any `td-*` skill the current release no longer ships is removed on update. Author your own skills under your **own prefix** (e.g. `mystudio-foo`); anything named `td-*` is owned by this system and may be replaced or deleted without warning.

Three separate pieces work together:

- **Skills** — reusable TouchDesigner workflow instructions (this repo)
- **MCP** — the live TDMCP connection to TouchDesigner (configured per host, see below)
- **Plugins/extensions** — provider-specific packaging (currently Claude Code only)

## Supported hosts

| Host | Skills location | MCP config |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` · `.claude/skills/` | `.mcp.json` / `~/.claude.json` (plugin auto-registers) |
| Codex | `~/.codex/skills/` · `.agents/skills/` | `~/.codex/config.toml` |
| Antigravity (`agy`) | `~/.gemini/antigravity-cli/skills/` · `.agents/skills/` | `~/.gemini/config/mcp_config.json` |
| OpenCode | not located | `opencode.json` |

Each row is the global path followed by the project path. In practice there are two project
roots: `.claude/skills/` for Claude Code and `.agents/skills/` for Codex and Antigravity, which
share it — so one project install serves both. Note `~/.agents/skills/` (the home-directory
form) is read by nothing; only the project-relative `.agents/` is real.

Gemini CLI was retired by Google on 2026-06-18 and replaced by Antigravity (`agy`), so it is
no longer a target. Legacy access continues only for enterprise licences and direct paid API
keys.

## Requirements

- One of the supported agent CLIs above
- [TDMCP](https://github.com/TouchDesigner/TDMCP) installed and running in TouchDesigner
- Python 3.7+ (only for the script install path)

## Quick install

```bash
git clone https://github.com/TouchDesigner/TDMCPSkills.git
cd TDMCPSkills
python install.py install --target claude
```

Pick the target that matches your CLI (see **Install targets** below). Project-local instead
of global:

```bash
python install.py install --target codex --project /path/to/your/project
```

Installing skills does **not** configure the MCP connection — do that once per host (next section).

## TDMCP MCP configuration

TDMCP serves MCP over HTTP at `http://127.0.0.1:13316/mcp`. Start it inside TouchDesigner before using any agent.

**Claude Code** — project `.mcp.json` (or `~/.claude.json`):

```json
{
  "mcpServers": {
    "tdmcp": { "type": "http", "url": "http://127.0.0.1:13316/mcp" }
  }
}
```

**Codex** — `~/.codex/config.toml`:

```toml
[mcp_servers.touchdesigner]
url = "http://127.0.0.1:13316/mcp"
```

**Antigravity (`agy`)** — global `~/.gemini/config/mcp_config.json`, or carried by a plugin
at `<project>/.agents/plugins/<name>/mcp_config.json` and registered with
`agy plugin install <path>`:

```json
{
  "mcpServers": {
    "touchdesigner": { "serverUrl": "http://127.0.0.1:13316/mcp" }
  }
}
```

`agy mcp list` shows only the global file — plugin-provided servers appear in the interactive
TUI's MCP Servers panel instead, with their tools namespaced `<plugin>_<server>`.

**OpenCode** — project `opencode.json` (or `~/.config/opencode/opencode.json`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "tdmcp": { "type": "remote", "url": "http://127.0.0.1:13316/mcp", "enabled": true }
  }
}
```

## Install — Claude Code plugin (recommended for Claude Code)

In Claude Code:

```
/plugin marketplace add TouchDesigner/TDMCPSkills
/plugin install tdmcp-skills@touchdesigner
```

This installs the 19 distributed skills and auto-registers the TDMCP MCP connection. Update with `/plugin marketplace update touchdesigner`; uninstall with `/plugin uninstall tdmcp-skills`.

Script alternative for Claude Code:

```bash
python install.py install --target claude
```

## Install targets

```bash
python install.py install --target claude        # ~/.claude/skills/  (Claude Code)
python install.py install --target agy           # ~/.gemini/antigravity-cli/skills/  (Antigravity)
python install.py install --target all           # claude + codex + agy
python install.py install --target others        # codex + agy (everything except Claude Code)
python install.py install --target codex         # ~/.codex/skills/   (Codex; project scope is .agents/skills/)

python install.py status --target claude         # install status + update check
python install.py uninstall --target claude
```

Notes:

- Each target keeps its own manifest; install/status/uninstall never touch another target.
- The installer only ever removes skill directories recorded in its own manifest. Conflicting `td-*` directories it doesn't own stop the install with an error (override with `--replace`).
- Pick **one primary target per host** — installing the same skills in multiple discovery locations can produce duplicates. `status` reports other known installs.
- Running `install.py` with no `--target` defaults to `claude`.
- **One project install can serve two hosts.** Codex and Antigravity both read
  `<project>/.agents/skills/`, so a single project-scope install covers both. Their
  global paths differ (`~/.codex/skills/` vs `~/.gemini/antigravity-cli/skills/`), so
  user-scope installs stay separate.
- If no local repo is detected, `install.py install` fetches the latest from GitHub directly.

### Migrating an existing `~/.claude/skills` install

Nothing breaks: `--target claude` preserves the previous behavior exactly. To also use another host, run that host's target as well (e.g. `--target codex`). Each target keeps its own manifest, so the installs are independent.

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
python install.py install --target claude   # or codex / agy / all / others
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

### Contributor skills

Contributor-only skills live in this repo's `.claude/skills/` and auto-load only when Claude Code is working inside a clone of TDMCPSkills. They are **not** distributed via the plugin or `install.py`.

**`/td-skills-local`** — legacy helper for installing skills into a specific project's `.claude/skills/`. Mostly superseded by the plugin install path.

## Compatibility notes

- Shared skill content is provider-neutral: MCP tool names are unqualified (`get_help`, not a host-prefixed name) because each host namespaces tools differently.
- Skill discovery and activation behavior varies by host; if a host doesn't auto-activate a skill, ask the agent to read the relevant `SKILL.md` explicitly.
- Smaller/local models (tested: qwen3:14b via OpenCode + Ollama) discover and load skills but tend to skip the cross-cutting `td-general` skill and jump straight to a builder skill, losing naming and get-help-first conventions. Mitigate by instructing "load `td-general` first" explicitly in the project's agent instructions (`AGENTS.md`).
- LM Studio is out of scope.

## Contributors

- Jarrett Smith (Derivative)
- Tim Gerritsen (y=f(x) Lab)
