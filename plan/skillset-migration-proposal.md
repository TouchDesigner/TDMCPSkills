# Skillset Migration Proposal — `darien` branch

**Status:** proposal for maintainer review
**Date:** 2026-06-13
**Branch:** `darien` (from `main` @ 1.1.1)
**Author:** Darien

## Purpose

This branch proposes adopting content from a **production TouchDesigner skillset** that has been maintained and used daily, and has diverged from — and matured well past — the current repo. This document is the evidence: a per-skill audit comparing the two trees, so maintainers can judge what is worth merging upstream and on what terms.

It is intentionally two-sided: the production set wins most comparisons, but `main` has one genuinely better skill and one original idea worth keeping. Both are called out.

## The two trees

| | **A — Production set** | **B — Current repo (`main`)** |
|---|---|---|
| Location | `D:\Dropbox\Claude\skills\touchdesigner` (independent repo, junction-installed) | `TDMCPSkills` `main` @ 1.1.1 |
| Skill dirs | **30** sub-skills | **18** distributed (+2 contributor in `.claude/`) |
| Architecture | Dispatcher: top-level `SKILL.md` with routing table, phase-gating (`pre/during/post-build`), proactive rules, disambiguation | Flat skills; routing in `CLAUDE.md`/`SKILLS.md` |
| Deep content | `references/` + `examples/` **subfolders** (load-on-demand, many small files) | Single flat `reference.md` / `examples.md` per skill |
| GLSL | **4 skills**: `td-glsl-{tops,compute,materials,pops}` (~68 KB / 27 files) | **1 merged** `td-glsl-shaders` (~14 KB / 3 files) |
| Cross-refs | `[[skill-name]]` wikilinks, dispatcher-resolved | none |
| Tooling | log hook, session analyzer, `validate_all.py`, `routing_test.py` (30 assertions), graph emitter, budget enforcer w/ exceptions | `validate.py` (portable contract); no contributor learn-tooling |

## Methodology

Per-skill content audit via parallel subagents, one comparison unit per skill pair, each reporting what either side has that the other lacks plus a stronger-side verdict on accuracy / actionable depth / pitfall coverage / token economics. 18 shared-name skills + the GLSL reorg were compared file-by-file. Findings below.

## Headline

Of 18 shared skills + the GLSL set: **production set stronger on ~12, tie on ~6, repo stronger on 1.** The production set is a near-superset in coverage and carries substantially more hard-won, non-obvious failure-mode knowledge (the kind that only accumulates through real builds).

## Net-new skills — exist in production set, absent from repo (12)

These have no equivalent in `main` and represent the bulk of the migration value:

| Skill | What it covers | Size |
|---|---|---|
| `td-cpp-chop` | C++ CHOP plugin authoring | 12 KB SKILL + 20 KB `api.md` |
| `td-ui-builder` | Panel COMP / authored UI (HTML→Panel) | 12 KB + examples/refs |
| `td-network-builder` | Build networks via Python exec'd from a textDAT | 8 KB + pitfalls/template |
| `td-glsl-tops` | GLSL pixel/fragment for glslTOP | 12 KB + refs/examples |
| `td-glsl-compute` | GLSL compute shaders (workgroups, dispatch, readback) | 8 KB + refs/examples |
| `td-glsl-pops` | GLSL POP / Advanced POP / Copy POP | 8 KB + 12 KB API + 8 examples |
| `td-glsl-materials` | glslMAT vertex+pixel (Basic/Phong/PBR) | 4 KB + refs/examples |
| `td-param-lookup` | Operator parameter-lookup discipline (proactive) | 4 KB |
| `td-python-module` | Reusable Python module, src+TD dual-target | 8 KB |
| `td-script-chop` | Script CHOP Python callback | 4 KB |
| `td-script-dat` | Script DAT Python callback | 4 KB |
| `td-script-sop` | Script SOP Python callback | 4 KB |

> The 4 GLSL skills collectively **replace and far exceed** the repo's single merged `td-glsl-shaders`. As discrete skills they are net-new; as coverage they close real gaps (compute workgroup math, POP topology API, Copy POP, picking, worked examples).

Plus migration-grade infrastructure (contributor side): the production `td-learn` ships a full observability + CI stack (session log hook, analyzer, structural validator, routing-test harness, dependency-graph emitter, budget enforcer); the repo ships no equivalent (its contributor `td-learn` was removed as out-of-scope for the public distribution). Note: the production stack's session-logging hook is exactly the kind of advanced setup the repo intentionally avoids — any port must keep it opt-in.

## Per-skill quality comparison — 18 shared skills

| Skill | Stronger | Decisive difference |
|---|---|---|
| td-build-planning | **A** | +baseCOMP-wiring IndexError pitfall, +"porting/mirroring an existing COMP" section |
| td-node-layout | **B** | Repo keeps "prefer single Y=0 row; feeder chains merge at Y=0, not a separate row" — A dropped it |
| td-network-cleanup | **A** | +Titletext/Bodytext annotation split (B dumps long text into unreadable title) |
| td-review-network | Tie | Near-identical; A adds `[[td-performance-check]]` link |
| td-performance-check | Tie | Functionally identical; A has `phase` frontmatter |
| td-comp-architecture | Tie (slight A) | A adds `[[td-ui-builder]]` crosslink; no technical delta |
| td-chop-family | Tie (slight A) | Same content; A modular (load-on-demand) + crosslinks |
| td-top-family | **A** | +4 hard gotchas B lacks: phantom glslTOP DATs, sibling-path silent-fail, constantTOP/noiseTOP 3D trap, alpha-corrupts-framebuffer |
| td-pop-family | **A** | +`Color`-not-`Cd` + `cullface=neither` pitfalls + modular *(B has 2 small uniques — see below)* |
| td-sop-family | Tie | Byte-equivalent; both intentionally thin |
| td-dat-family | **A** | +empty-`pars`-silently-inert, +parameterexecuteDAT next-cook timing |
| td-mat-family | **A** | +`lineMAT` coverage + 2 line width/color pitfalls; B has no lineMAT |
| td-geometry-instancing | **A** | +direct-POP instancing path (B forces poptoCHOP → needless GPU→CPU per build) |
| td-python-extension | **A** | +`TDF.createProperty`, `StorageManager`, dependable state (13 vs 3 refs) |
| td-lister-ui | Tie | Reference files identical |
| td-learn | **A** | Production has a full observability + CI stack; repo ships none (contributor `td-learn` removed) |
| td-skills-local | Tie | Functionally identical |
| **GLSL** (1 vs 4) | **A** | ~68 KB/27 files vs 14 KB/3; B's merge surface-level on compute/materials/pops, no examples |

## What `main` does better (keep / don't regress)

Credibility check — the repo is not strictly dominated:

1. **`td-node-layout`** — main's "prefer a single Y=0 row; feeder chains merge at Y=0 left of the merge, not on a separate row" is actionable layout guidance the production set lost in compression. **Back-port into the production set.**
2. **Collaborative framing (original to main)** — main recently added a **`td-chill`** skill + a `## Your Role` "thinking-partner, not a builder" section in `td-general` (ask before building, build small discussable steps). The production set has none of this; its `td-general` went toward token-economics and failure-mode gotchas instead. This is a philosophy main owns — **worth preserving through any merge**, not overwritten.
3. Minor GLSL gotchas main flags that need a verify-pass against the production set's 27 GLSL files before discarding: glslPOP `vec` vs `const` recompile behavior; `glslmultiTOP` has no `resolution` par (errors + halts `build_network`); `me.time.step` doesn't exist (use `1.0/me.time.rate`).

## Structural decisions for maintainers

Migration is not a straight copy. The two trees encode different distribution models; merging requires choosing:

1. **Dispatcher vs flat.** *Resolved — see "Architecture: dispatcher vs flat" below.* Short version: keep flat as the canonical portable content; routing is implemented as a validator-enforced **Skill Map** in `td-general` (done on `darien`), not a separate dispatcher skill. A full dispatcher adapter remains optional.
2. **`references/` subfolders vs flat `reference.md`.** Production uses many small load-on-demand files; repo uses one file per skill. Subfolders lower per-task token load but add file count. `validate.py`'s portable contract would need to accept the subfolder layout.
3. **Wikilinks.** `[[skill-name]]` cross-refs assume the dispatcher resolver. In the flat/portable model these must degrade gracefully (plain names) — `validate.py` already checks reference resolvability.
4. **GLSL: 4 split skills vs 1 merged.** Real tradeoff — split = lower token-load per task + better discovery; merged = fewer files. Audit favors the split on coverage, but this is a maintainer call.
5. **Provider-neutrality.** Production content was authored for Claude Code; the repo's contract forbids provider-specific tool names/paths in shared content. A neutrality pass (`validate.py`) is required before upstreaming.

## Architecture: dispatcher vs flat

"Better" depends on the goal. The **dispatcher** optimizes for deterministic, correct routing in one strong host (Claude Code, expert, complex builds). The **flat** model optimizes for portable distribution across hosts with varying skill-discovery quality. Each is the right tool for its tree's mission.

| Dimension | Dispatcher | Flat | Edge |
|---|---|---|---|
| Routing | Explicit always-loaded intent→skill table | Implicit host description-matching + `CLAUDE.md`/`SKILLS.md`/`td-general` | Dispatcher (deterministic) |
| `td-general`-skip failure | Structurally prevented (router enforces load-first) | **Documented failure** — small models skip it, lose conventions | Dispatcher |
| Phase gating (no cleanup mid-build) | Built in (`pre`/`during`/`post-build`) | Described, not enforced | Dispatcher |
| Disambiguation ("GLSL"→which of 4) | Explicit rules | None | Dispatcher |
| Host portability | One skill; routing relies on agent obeying Read instructions | Each skill rides host **native** discovery (Codex/Gemini/OpenCode) | Flat (the repo's reason to exist) |
| Scaling / maintenance | Add skill = edit central routing table (`routing_test.py` guards) | Add skill = drop folder w/ good `description` | Flat (decoupled) |
| Spec conformance | Custom convention on top of Agent Skills | Matches Anthropic Agent Skills spec | Flat |

Minor: dispatcher pays a ~2K-token router on every TD intent (always-on) and offers richer `[[wikilink]]` cross-refs; flat has a lower, less predictable token floor and plain self-resolving refs only.

**Key insight — routing is metadata, not content.** Sub-skill *content* (the TD knowledge) is identical regardless of how it's routed. Routing is a thin layer on top, so the two models are **separable and stackable**, not mutually exclusive:

```
Canonical layer:   flat td-* skills (portable, spec-conformant)   ← single source of truth
Optional adapter:  dispatcher SKILL.md that routes among them     ← Claude-Code-only, opt-in
```

A Claude Code user installs the dispatcher → gets explicit routing + phase-gating + disambiguation. A Codex/Gemini/OpenCode user installs the flat skills → gets native discovery. Same content, two front-ends. `validate.py` treats the dispatcher as a host adapter (like the plugin packaging already is).

**Resolution:** stay **flat-canonical** for portability; preserve the dispatcher's routing intelligence (phase-gating, disambiguation, load-first enforcement) as an **opt-in Claude-Code adapter**. This is also the direct answer to the maintainer's biggest objection ("we're multi-host, your dispatcher is single-host") — the proposal does not ask them to abandon flat; it adds a layer for the host that benefits, and the dispatcher's routing logic is the most valuable non-content asset in the production set.

**Update — implemented on `darien`:** rather than a separate always-on dispatcher skill, this repo's routing now lives as a **Skill Map** in `td-general` (intent → skill + phase, one bullet per skill), with `validate.py` enforcing map↔skills sync (every distributed skill has an entry; no stale entries). This delivers routing + phase discipline portably — it rides every host's native discovery, needs no always-on skill, and can't drift. A separate Claude-Code dispatcher adapter is therefore **not needed as a baseline**; it stays an option only if the personal set's disambiguation-heavy routing (4-way GLSL, script split) is later ported.

## Proposed migration path (phased, low-risk)

1. **Net-new builder skills first** — `td-cpp-chop`, `td-ui-builder`, `td-network-builder`, `td-script-{chop,dat,sop}`, `td-python-module`, `td-param-lookup`. Additive, no conflict with existing skills. Run `validate.py` per skill.
2. **GLSL** — land the 4-way split as new skills; deprecate/redirect `td-glsl-shaders`. Maintainer decision on split-vs-merge gates this step.
3. **Per-skill content merges** — fold the production gotchas into the 8 shared skills where A is stronger (top/pop/dat/mat/geometry-instancing/python-extension/build-planning/network-cleanup), preserving main's `td-chill` framing and the `td-node-layout` Y=0 rule. **Done on `darien`** — 8 universal nuggets back-ported (see git log).
4. **Tooling** — optionally adopt the production `td-learn` validator/CI stack (`validate_all.py`, `routing_test.py`, graph emitter) as contributor-side infrastructure.
5. **Neutrality + contract pass** — `validate.py` green across all migrated skills; adapt subfolder layout and wikilinks to the portable contract.
6. **Routing — done on `darien` via the Skill Map, not a separate dispatcher.** Native routing lives in `td-general`'s Skill Map (intent → skill + phase), enforced by `validate.py`. Portable, no always-on skill, can't drift. A separate Claude-Code dispatcher adapter is optional and only justified if the personal set's disambiguation-heavy routing is ported — not needed for the current 18-skill, merged-GLSL repo. See "Architecture: dispatcher vs flat".

## Bottom line

The production set is the more mature body of TouchDesigner knowledge — 12 net-new skills and a deep reserve of failure-mode gotchas the repo never captured. The cost is not content quality but **reconciling two distribution models** (dispatcher/subfolder/wikilink vs flat/portable). This branch exists to do that reconciliation in the open and stage it for review, while preserving the collaborative framing `main` contributed.
