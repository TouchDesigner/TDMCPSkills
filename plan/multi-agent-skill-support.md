# Multi-Agent Skill Support Plan

## Objective

Extend TDMCPSkills from a Claude Code-specific distribution into a portable
Agent Skills repository supporting:

- Claude Code
- Codex
- Gemini CLI
- OpenCode

Keep `skills/` as the canonical source of TouchDesigner workflow knowledge.
Treat provider-specific installation, MCP registration, and packaging as
adapters around that source.

LM Studio is explicitly out of scope.

## Guiding Decisions

1. Use the Agent Skills `SKILL.md` format as the shared content contract.
2. Use `.agents/skills/` as the preferred portable install location.
3. Retain `.claude/skills/` and the Claude plugin for Claude Code support.
4. Retain an optional Codex-specific target only where needed for compatibility.
5. Keep MCP configuration separate from skill installation.
6. Avoid provider-qualified MCP tool names in shared skill content.
7. Never modify or remove skills that are not owned by the TDMCPSkills manifest.

## Supported Targets

| Target | Global skills | Project skills | Notes |
| --- | --- | --- | --- |
| Portable agents | `~/.agents/skills/` | `.agents/skills/` | Preferred for Codex, Gemini CLI, and OpenCode |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | Preserve plugin and script compatibility |
| Codex legacy | `~/.codex/skills/` | Not required initially | Optional compatibility target |

Provider-native package or extension formats may be added later, but they must
consume the same canonical `skills/` directories.

## Phase 1: Establish the Shared Skill Contract

### Tasks

- Add a `name` field to every distributed `skills/*/SKILL.md` frontmatter.
- Ensure each name exactly matches its containing directory.
- Keep frontmatter limited to portable fields:
  - `name`
  - `description`
- Confirm names satisfy the common lowercase, digits, and hyphens convention.
- Make descriptions explicit enough for reliable automatic activation.
- Replace references to "Claude" in distributed skills with neutral terms such
  as "agent" or "host."
- Remove `/td-learn` from the distributed `td-general` workflow because it is a
  contributor-only Claude skill.
- Keep MCP tool references unqualified, for example `get_help` rather than a
  host-specific namespace.

### Acceptance Criteria

- Every distributed skill has valid `name` and `description` metadata.
- Directory name and frontmatter name match.
- Distributed skill bodies do not depend on Claude-only commands.
- The existing TouchDesigner MCP tool workflow remains unchanged.

## Phase 2: Add Cross-Provider Validation

### Tasks

- Add a repository validation command, preferably `validate.py`.
- Validate:
  - Every `skills/td-*` directory contains `SKILL.md`.
  - Frontmatter is valid YAML.
  - `name` and `description` are present.
  - Skill names match directory names.
  - Names meet the shared naming rules.
  - Descriptions are non-empty and within documented host limits.
  - Relative links from `SKILL.md` resolve.
  - Referenced `reference.md`, `examples.md`, and scripts exist.
  - No distributed skill contains known provider-only commands or paths.
- Make validation runnable without installing the skills.
- Add focused installer tests using temporary directories.

### Acceptance Criteria

- One command validates all distributed skills.
- Validation fails with actionable file and field diagnostics.
- Tests do not write to real user skill directories.

## Phase 3: Refactor the Installer Around Target Profiles

### Proposed CLI

```text
python install.py install --target agents
python install.py install --target claude
python install.py install --target codex-legacy
python install.py install --target all

python install.py install --target agents --project .
python install.py status --target agents
python install.py uninstall --target agents
```

Use `agents` as the recommended default after a migration period. Preserve the
current Claude behavior through an explicit `--target claude` option.

### Tasks

- Introduce a target profile abstraction containing:
  - Target identifier
  - Display name
  - Global path
  - Project-relative path
  - Restart or reload guidance
- Replace the hard-coded `.claude/skills` logic in `resolve_target`.
- Give each target its own manifest.
- Include target, version, source, and installed skill names in the manifest.
- Scope uninstall and upgrades strictly to skill names recorded in that
  target's manifest.
- Remove the current behavior that deletes every stale `td-*` directory when no
  manifest exists.
- Detect unmanaged name conflicts and stop with an actionable error unless an
  explicit replacement option is supplied.
- Preserve local-source and remote-source installation modes.
- Keep version-pinned installation behavior.
- Report the correct reload instruction:
  - Claude Code: restart or refresh the plugin/session.
  - Codex: restart Codex or start a new session as required.
  - Gemini CLI: reload skills or restart the session.
  - OpenCode: restart or refresh skill discovery.

### Acceptance Criteria

- Install, status, update, and uninstall work independently for every target.
- Installing one target does not alter another target.
- Existing unrelated skills are never deleted.
- Project installs resolve beneath the supplied project path.
- Existing Claude users have a documented migration path.

## Phase 4: Preserve and Isolate Provider Integrations

### Claude Code

- Preserve `.claude-plugin/plugin.json`.
- Preserve `.claude-plugin/marketplace.json`.
- Preserve automatic TDMCP registration through `.mcp.json`.
- Update descriptions from "Claude-only skills" to portable skills packaged for
  Claude Code.
- Verify the plugin still distributes all canonical `skills/` directories.

### Codex

- Document `.agents/skills/` as the preferred global and project location.
- Document `~/.codex/skills/` only as a compatibility target if testing shows it
  remains useful.
- Do not add a Codex plugin until the bundle needs more than skills and MCP
  documentation.
- Provide a tested TDMCP MCP configuration example separately from skill
  installation.

### Gemini CLI

- Document `.agents/skills/` discovery.
- Test activation and explicit skill listing.
- Consider documenting `gemini skills install` as an alternative distribution
  path after repository installation behavior is verified.
- Keep TDMCP MCP setup as a separate provider integration.

### OpenCode

- Document `.agents/skills/` discovery.
- Verify all skills appear through OpenCode's native skill tool.
- Document any required skill permissions.
- Keep TDMCP MCP setup separate from skills.

### Acceptance Criteria

- Provider-specific files are isolated from canonical skill content.
- Shared skills do not encode provider configuration.
- Every supported host has documented skill and MCP setup paths.

## Phase 5: Documentation and Migration

### README Structure

1. What TDMCPSkills provides
2. Supported agent hosts
3. Quick install using the portable `agents` target
4. Provider-specific installation
5. TDMCP MCP configuration
6. Updating, status, and uninstalling
7. Contributor workflow
8. Compatibility notes

### Tasks

- Rewrite Claude-only wording in `README.md` and `SKILLS.md`.
- Add a support matrix for the four hosts.
- Clearly distinguish:
  - Skills: reusable workflow instructions
  - MCP: live TouchDesigner tools
  - Plugins/extensions: provider-specific packaging
- Add migration instructions for existing `~/.claude/skills` users.
- Document conflict handling and manifest ownership.
- Update installer help text and examples.
- Decide whether this is a minor or major version change based on the default
  target migration.

### Acceptance Criteria

- A new user can identify the correct install command for their host.
- Existing Claude users can update without losing their installation.
- Documentation does not imply that installing skills configures MCP unless a
  provider package explicitly does so.

## Phase 6: Compatibility Test Matrix

### Content Validation

- Run repository validation.
- Verify every skill can be discovered from its metadata.
- Check all relative references and examples.

### Installer Tests

For each target:

- Fresh global install
- Reinstall same version
- Upgrade from an older manifest
- Status with all skills present
- Status with one skill missing
- Uninstall
- Project-local install and uninstall
- Unmanaged conflicting skill directory
- Multiple targets installed simultaneously

### Host Smoke Tests

Use the same TouchDesigner tasks across hosts:

1. Create a TOP processing chain.
2. Build an animated CHOP-driven control.
3. Create and compile a GLSL TOP.
4. Review an intentionally broken network.
5. Clean up and annotate a completed network.

Verify:

- Correct skills are discoverable.
- `td-general` and relevant builder skills activate.
- MCP tools are callable under the host's namespace.
- The agent checks errors and runtime output.
- No skill instructs the host to use unavailable provider commands.

### Acceptance Criteria

- All installer tests pass.
- Each supported host completes at least one build and one review workflow.
- Host-specific deviations are documented rather than embedded in shared
  skills unless unavoidable.

## Phase 7: Release and Rollout

### Tasks

- Land metadata and content-neutrality changes first.
- Land validation before changing installer behavior.
- Add target profiles while preserving the Claude target.
- Run the full compatibility matrix.
- Update `VERSION` and both Claude plugin version fields together.
- Publish release notes with:
  - New supported hosts
  - New install commands
  - Default-target behavior
  - Claude migration instructions
  - MCP configuration boundaries

### Rollback Strategy

- Keep the previous Claude-only release tag available.
- Preserve `--target claude` throughout the initial portable release series.
- Avoid moving or renaming canonical skill directories during the migration.

## Suggested Implementation Order

1. Add `name` metadata and neutralize shared skill wording.
2. Add `validate.py` and temporary-directory installer tests.
3. Refactor `install.py` to support target profiles.
4. Fix manifest ownership and conflict behavior.
5. Update Claude packaging metadata without changing plugin behavior.
6. Rewrite README and SKILLS documentation.
7. Run host smoke tests.
8. Version and release.

## Risks

### Provider specifications may change

Keep target paths and provider instructions in small adapter definitions and
documentation sections. Do not duplicate skill content per provider.

### Shared skills may reference host-specific behavior

Catch known provider terms in validation and test realistic workflows on every
host.

### Installer upgrades could delete user-managed skills

Only remove paths listed in the TDMCPSkills manifest. Treat unmanaged conflicts
as errors by default.

### Installing the same skills in multiple discovery locations can create
duplicates

Recommend one primary target per user. Report duplicate known installations in
`status` without deleting them automatically.

### Smaller or local models may struggle with the full workflow

Keep skills concise, preserve progressive disclosure, and move detailed
material into references instead of creating model-specific copies.

## Out of Scope

- LM Studio integration
- Rewriting skills for individual model families
- Bundling or installing the TDMCP server itself
- Automatically editing every provider's MCP configuration by default
- A universal plugin marketplace abstraction
- Contributor-only `.claude/skills` migration in the initial release

## Definition of Done

- All canonical skills conform to the shared Agent Skills metadata contract.
- Claude Code, Codex, Gemini CLI, and OpenCode have supported installation
  paths.
- The installer manages each target independently and safely.
- Shared skill content is provider-neutral.
- Validation and installer tests run successfully.
- The compatibility smoke-test matrix passes.
- Documentation clearly separates skills, MCP configuration, and
  provider-specific packaging.
