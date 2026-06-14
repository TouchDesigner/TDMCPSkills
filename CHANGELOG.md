# Changelog

All notable changes to TDMCPSkills are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this
project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Released
versions are tracked in `VERSION` and the Claude plugin manifests.

## [Unreleased]

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
  `td-chill`).

### Fixed
- `validate.py` — the stray-directory check no longer fails on hidden/dot
  directories under `skills/` (e.g. a tool-created `.claude/`).
