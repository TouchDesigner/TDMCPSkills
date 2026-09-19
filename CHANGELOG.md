# Changelog

All notable changes to TDMCPSkills are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this
project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Released
versions are tracked in `VERSION` and the Claude plugin manifests.

## [Unreleased]

### Added
- **`hosts.py`** — shared agent-host registry: one `Host` record per agent CLI holding
  its skills strategy (`copy_dir` / `cli` / `none`), discovery paths, scope vocabulary,
  MCP add/remove/login command templates, and a `verified` stamp naming the CLI version
  its claims were last tested against. `install.py` and TDMCP's in-component installer
  both read it, so supporting a new agent is a one-record change.
- Host records for `gemini` (0.46.0 — `~/.gemini/skills/`, scopes `user|workspace`),
  `codex` (0.155.0 — no skills mechanism; global-only MCP config, `mcp login` for auth), and
  `agy` (Antigravity CLI 1.2.7 — global MCP config, `agy mcp add <name> <url>` with the
  scheme auto-detected; no skills mechanism located, so skill installs refuse rather than
  guess a path).
- Gemini is **not** deprecated — only its Homebrew formula is, which is why `brew upgrade`
  stalls at 0.46.0. npm `@google/gemini-cli` is actively released (0.60.0 stable, nightlies
  current). Install it from npm, not brew.
- `--target gemini`. A directory copied straight into `~/.gemini/skills/` is discovered with
  no CLI step, so the existing copy installer serves Gemini unchanged; `gemini skills link`
  is an alternative that symlinks a checkout into that same directory.

### Changed
- **`agy` gained its skills paths**, from the official docs at antigravity.google/docs/skills
  and corroborated by strings in the binary: `~/.gemini/antigravity-cli/skills/` globally and
  `<workspace>/.agents/skills/` per project, both plain directory copies. Not probe-confirmed:
  `agy -p` does not enumerate skills (a control marker in its own `builtin/skills/` came back
  empty too), and they surface as `/<skill-name>` in the interactive TUI.
- **`codex` is a skills host after all.** The record previously said Codex had no skills
  mechanism, because `codex --help` has no `skills` subcommand. A probe disproved it: an
  identical marker skill placed in `~/.codex/skills/` **and** in `<project>/.agents/skills/`
  was named back by `codex exec` from both. Note the project path is the cross-agent
  `.agents/skills/`, not `.codex/skills/`.
- **`codex-legacy` retired into `codex`.** It claimed the same `~/.codex/skills/` path,
  unverified, and two records on one directory make `status` report an install twice and let
  one host's prune sweep delete the other's skills. Anyone who installed with
  `--target codex-legacy` can uninstall with `--target codex` — same directory, same manifest.
- `install.py` no longer defines its own target table; `--target` choices are now the
  registry's directory-copying hosts.
- **`--target all` installs to `claude` only** (was `agents` + `claude`). `~/.agents/skills/`
  has not been confirmed as any host's discovery path, so `all` no longer creates it.
  `--target agents` still works explicitly.

### Removed
- **The `agents` target.** `~/.agents/skills/` was recorded as a portable location shared by
  Codex, Gemini CLI and OpenCode. Probed: Claude Code reads neither `~/.agents/skills/` nor
  `<project>/.agents/skills/` (confirmed against a control skill in `.claude/skills/`), Gemini
  reads its own `~/.gemini/skills/`, and the only host found reading `.agents/skills/` is Codex
  — project-scope only, which the `codex` record now covers. The record also collided with
  `codex` on `<project>/.agents/skills/`, so skill status reported one host's install under the
  other's name. `--target agents` is gone; use `--target codex` or `--target agy`.

### Fixed
- `status` crashed with a `TypeError` when the registry contained a host without a
  global skills path.

## [1.3.0] - 2026-09-18

Supersedes the 1.2.3 stamp that sat in `VERSION` and the plugin manifests without
ever being released: `td-working-mode` is a whole new skill, and under SemVer a new
feature is a minor bump, not a patch.

### Added
- **`td-working-mode`** — new cross-cutting posture skill: capability routing
  (text/code-on-disk + empirical verification vs. blind spatial node-building), the
  code-on-disk mechanic, "close every loop by looking", and a drift trigger with a
  `/td-working-mode` re-entry line. Sibling to `td-colab`.
- `td-general` — a **Working Posture** stub (ambient capability-routing guidance),
  plus a Skill Map row and `SKILLS.md` listing for `td-working-mode`.
- `td-glsl-shaders` — document the glslTOP/glslMAT **Colors** page (`color0name` +
  `color0rgbr/g/b` + `color0alpha`) for `vec4` color uniforms, distinct from the
  Vectors page; note the **Samplers**/**Arrays** pages alongside it.
- `td-pop-family` — two live-verified pitfalls: forceradialPOP `globforcemult`
  defaults to 0 (Global Force silently inert), and mathmixPOP `combN` scope/result
  pars stay disabled until that block's oper is set.
- `td-general` — a **Get Docs** section: when to reach for `get_docs` (TD Python
  API, concept articles) vs `get_help` (live parameter names/menus), plus `section`
  drill-down so class pages don't arrive whole (~10K tokens with inlined inheritance).

### Changed
- `td-colab` — added a **Sibling** section cross-linking `td-working-mode` as the
  capability self-awareness beneath the collaboration ethic.

## [1.2.2] - 2026-06-16

Merges the `darien` 1.2.0/1.2.1 release work with the `td-chill` → `td-colab`
rename and code-on-disk skill expansions that landed on `main` (internal `1.1.2`).

### Changed
- **Renamed `td-chill` → `td-colab`** (collaborative thinking-partner mode). The
  skill directory, its `name`/description, the `td-general` Skill Map row, and all
  doc references now use `td-colab`. The `/td-colab` command resets the
  collaborative frame.
- Expanded code-on-disk mechanics — DAT↔file sync flow, Content Language, and the
  extension recipe — in `td-dat-family`, `td-glsl-shaders`, and
  `td-python-extension`.

### Fixed
- Reconciled the rename with the new `validate_skill_map()` check introduced in
  1.2.0: with the skill renamed to `td-colab`, the Skill Map's stale `td-chill`
  row would have failed validation (`no row for distributed skill 'td-colab'` /
  `lists 'td-chill' which is not a distributed skill`). The map now lists
  `td-colab`; `validate.py` is green.

## [1.2.1] - 2026-06-14

### Removed
- `td-learn` contributor skill (`.claude/skills/td-learn/` + `skill_stats.py`) and
  all references (README, SKILLS.md, CLAUDE.md workflow, `validate.py` guard) —
  out of scope for the public distribution; it was contributor-only tooling.
  Skill-size budgeting stays a manual `CLAUDE.md` guideline.

### Fixed
- Ignore tool-created `skills/.claude/` analytics logs so the canonical skills
  source stays adapter-free (`.gitignore`).

## [1.2.0] - 2026-06-13

### Added
- **Skill Map** in `td-general` — an intent → skill routing list (one bullet per
  skill) with phase tags (`pre`/`during`/`post-build`/`anytime`) covering all 18
  skills, making `td-general` the explicit routing anchor.
- `validate.py` — Skill Map sync check: every distributed skill must have a map
  entry and every entry must point to a real skill (the build fails on drift).
- Universal TouchDesigner gotchas back-ported into existing skills:
  - `td-top-family` — phantom glslTOP companion DATs, sibling-path silent-fail,
    constantTOP/noiseTOP 3D-mode trap, alpha-corrupts-framebuffer
  - `td-pop-family` — render color attr is `Color` (not `Cd`); `cullface=neither`
    for filled geometry
  - `td-dat-family` — empty `pars` silently inert; parameterexecuteDAT fires next cook
  - `td-mat-family` — `lineMAT` material type + per-line color and width pitfalls
  - `td-geometry-instancing` — direct-POP instancing path (avoids GPU→CPU)
  - `td-python-extension` — State & Persistence (`TDF.createProperty`,
    `StorageManager`, dependable state)
  - `td-build-planning` — `build_network` baseCOMP connection-order `IndexError`
  - `td-network-cleanup` — Titletext vs Bodytext annotation split
- `CHANGELOG.md` — this file.

### Changed
- `td-general` — description strengthened as the always-first anchor and now
  references the Skill Map; Workflow builder list de-duplicated to defer to it.
- Skill descriptions tightened for discovery triggering: `td-performance-check`
  (added a "use when" trigger), `td-glsl-shaders` (+POP), `td-mat-family`
  (+lineMAT), `td-python-extension` (+state/persistence).
- `README.md` — corrected the distributed skill count from 17 to 18 (counts
  `td-colab`, renamed from `td-chill` in 1.2.2).

### Fixed
- `validate.py` — the stray-directory check no longer fails on hidden/dot
  directories under `skills/` (e.g. a tool-created `.claude/`).
