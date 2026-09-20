#!/usr/bin/env python3
"""Agent host registry — one record per agent CLI.

Single source of truth for how each host discovers skills and how it registers
the TDMCP server. Both installers read it: `install.py` (standalone CLI) and
TDMCP's in-component `SkillsInstaller.py`. Supporting a new agent means adding
one `Host` record here and nothing else.

Client CLIs move fast and their conventions drift, so every record carries a
`verified` stamp naming the CLI version its claims were last tested against.
Treat a record stamped `unverified` as a hypothesis, not a fact — re-test and
update the stamp rather than trusting the entry.

Skills strategies:
    copy_dir  host discovers a directory of skill folders; the installer copies
              them in (Claude Code, and the portable ~/.agents layout)
    cli       host owns a skill registry behind its own CLI; installing means
              shelling out to that CLI (Gemini)
    none      host has no skills mechanism; skills reach it only as prose in an
              AGENTS.md-style context file (Codex, OpenCode)
"""
from pathlib import Path

UNVERIFIED = 'unverified'


class Host:
    """One agent host: where its skills live, and how it adds the MCP server."""

    def __init__(self, ident, display, *, skills='copy_dir',
                 global_path=None, project_subpath=None,
                 link_cmd=None, unlink_cmd=None, scope_names=None,
                 mcp_add=None, mcp_remove=None, mcp_auth=None,
                 mcp_scope='global', reload_hint='', verified=UNVERIFIED):
        self.ident = ident
        self.display = display
        self.skills = skills
        self.global_path = global_path          # Path or None
        self.project_subpath = project_subpath  # str or None (None = global only)
        self.link_cmd = link_cmd                # skills='cli' only
        self.unlink_cmd = unlink_cmd            # skills='cli' only
        # Canonical scope -> this host's own word for it. Gemini says
        # "workspace" where everyone else says "project".
        self.scope_names = scope_names or {'user': 'user', 'project': 'project'}
        self.mcp_add = mcp_add                  # template with {url}
        self.mcp_remove = mcp_remove
        self.mcp_auth = mcp_auth                # follow-up when Auth is on
        self.mcp_scope = mcp_scope              # 'project' or 'global'
        self.reload_hint = reload_hint
        self.verified = verified

    # -- skills -------------------------------------------------------------

    @property
    def copies_skills(self):
        """True when this host is served by copying skill folders into a dir."""
        return self.skills == 'copy_dir'

    def resolve(self, project_path=None):
        """Skills directory for this host, global unless project_path is given.

        Raises ValueError when asked for a scope the host does not support, so
        callers decide how to report it (CLI prints and exits; TD sets status).
        """
        if not self.copies_skills:
            raise ValueError(
                f"host '{self.ident}' does not install skills by copying "
                f"(strategy: {self.skills})")
        if project_path:
            if not self.project_subpath:
                raise ValueError(
                    f"host '{self.ident}' does not support project installs")
            return Path(project_path).resolve() / self.project_subpath
        if self.global_path is None:
            raise ValueError(f"host '{self.ident}' has no global skills path")
        return self.global_path

    def scope_label(self, scope):
        """This host's own word for a canonical scope ('user' / 'project')."""
        return self.scope_names.get(scope, scope)

    # -- MCP connection -----------------------------------------------------

    def mcp_command(self, scheme='http', port=13316, auth=False,
                    address='127.0.0.1'):
        """The one-liner that points this host at a running TDMCP server.

        Covers every connection state the component exposes: `scheme` follows
        Usehttps, `port` follows Port, `auth` follows Auth. Returns None for
        hosts with no known MCP command.
        """
        if not self.mcp_add:
            return None
        cmd = self.mcp_add.format(url=f'{scheme}://{address}:{port}/mcp')
        if auth and self.mcp_auth:
            cmd += f' && {self.mcp_auth}'
        return cmd


HOSTS = {
    'agy': Host(
        'agy',
        'Antigravity CLI',
        global_path=Path.home() / '.gemini' / 'antigravity-cli' / 'skills',
        # Shared with codex — see SHARED_PROJECT_ROOT below.
        project_subpath='.agents/skills',
        mcp_add='agy mcp add touchdesigner {url}',
        mcp_remove='agy mcp remove touchdesigner',
        mcp_scope='global',
        reload_hint=('Skills become /<skill-name> in the interactive TUI; headless -p does '
                     'not enumerate them. Confirm there, not with `agy -p`.'),
        # 1.2.7. Paths from the official docs (antigravity.google/docs/skills),
        # corroborated by strings in the binary (.agents/skills x12) and by agy
        # itself reporting its workspace roots. A copied directory is discovered at
        # ~/.gemini/antigravity-cli/skills/ (global) or <workspace>/.agents/skills/
        # (project); plugins may also carry skills/. SKILL.md needs a `description`;
        # `name` defaults to the folder.
        #
        # `_agents/skills` is a real alias (x2 in the binary) but not the primary
        # form. agy also claimed `.agent/` and `_agent/` roots; neither appears in
        # the binary, so treat those as unsupported — an agent describing its own
        # paths is a claim, not evidence, same class as docs.
        #
        # Skills placed in .gemini/skills/ are NOT auto-mounted by agy; it can read
        # them as files but they do not become /<skill-name>. That is why gemini and
        # agy stay separate records despite sharing the ~/.gemini root.
        #
        # PROJECT PATH CONFIRMED 2026-09-19: skills installed to
        # <workspace>/.agents/skills/ mount in the interactive TUI, checked in a
        # folder where .agents was the only agent root. The GLOBAL path is still
        # documented-only — headless cannot list skills, and a control marker in
        # agy's own builtin/skills/ came back empty, so that test was
        # uninformative rather than negative. Probe the global path separately
        # before trusting it; evidence for one path is not evidence for both.
        # MCP: `agy mcp add [flags] <name> <commandOrUrl>`, http/https auto-detected,
        # config is global at ~/.gemini/config/mcp_config.json (verified).
        verified='agy 1.2.7, 2026-09-19 (MCP + project skills probed; global skills path documented only)',
    ),
    'claude': Host(
        'claude',
        'Claude Code',
        global_path=Path.home() / '.claude' / 'skills',
        project_subpath='.claude/skills',
        mcp_add='claude mcp add --transport http touchdesigner {url}',
        mcp_remove='claude mcp remove touchdesigner',
        mcp_scope='project',
        reload_hint='Restart Claude Code or start a new session to pick up skill changes.',
        verified='claude-code, in daily use 2026-09-18',
    ),
    'codex': Host(
        'codex',
        'Codex',
        global_path=Path.home() / '.codex' / 'skills',
        # Codex reads a PROJECT-relative .agents/skills — the cross-agent root —
        # not .codex/skills inside the project. Verified by probe, see below.
        project_subpath='.agents/skills',
        mcp_add='codex mcp add touchdesigner --url {url}',
        mcp_remove='codex mcp remove touchdesigner',
        mcp_auth='codex mcp login touchdesigner',
        mcp_scope='global',
        reload_hint='Restart Codex or start a new session to pick up skill changes.',
        # 0.155.0: there is no `skills` subcommand, which is why this record once
        # said the host had no skills mechanism. A probe proved otherwise: an
        # identical marker skill placed in ~/.codex/skills/ AND in
        # <project>/.agents/skills/ was named back by `codex exec` from both.
        # ~/.codex/skills/ is Codex-owned (it keeps a .system entry there).
        # MCP: `mcp add` has no scope flag and writes ~/.codex/config.toml; a
        # project-local .codex/config.toml is NOT auto-discovered (tested with and
        # without trust_level="trusted"). CODEX_HOME=./.codex does load one.
        verified='codex-cli 0.155.0, 2026-09-18 (skills + MCP both probed)',
    ),
    'opencode': Host(
        'opencode',
        'OpenCode',
        skills='none',
        mcp_add='opencode mcp add touchdesigner --url {url}',
        mcp_remove='opencode mcp remove touchdesigner',
        mcp_scope='global',
        reload_hint='OpenCode reads a project ./opencode.json if you create one.',
        # 1.17.7: no `skills` subcommand. MCP command shape not re-tested.
        verified=UNVERIFIED,
    ),
}

# Codex and Antigravity both read <project>/.agents/skills, so ONE project-scope
# install serves both. Kept as separate records because their global paths differ
# (~/.codex/skills vs ~/.gemini/antigravity-cli/skills).
SHARED_PROJECT_ROOT = {'codex', 'agy'}

# `all` means "put the skills wherever a supported agent will look for them".
# Every host here has a discovery path we established by probe.
ALL_HOSTS = ['claude', 'codex', 'agy']

# Two roots matter in practice: .claude/ and .agents/. These presets are the
# choices that actually differ, so the in-TD install is one meaningful pick
# rather than a per-host menu.
PRESETS = {
    'all': ALL_HOSTS,
    'others': [h for h in ALL_HOSTS if h != 'claude'],
}


def expand_hosts(name):
    """Host records for a preset name or a single host ident."""
    return [HOSTS[h] for h in PRESETS.get(name, [name])]


def copy_hosts():
    """Idents of hosts a directory-copying installer can serve."""
    return [ident for ident, h in HOSTS.items() if h.copies_skills]
