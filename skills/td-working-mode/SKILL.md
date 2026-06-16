---
name: td-working-mode
description: Working posture — route work to the agent's strengths (code-on-disk + empirical verification) and away from blind spatial node-building. Load when building, or when you catch yourself placing nodes by guesswork. Sibling to td-colab.
---

# Working Mode — route to where your senses reach

A posture skill: get into the state where this agent works best in TouchDesigner.
Sibling to `td-colab`. td-colab is the *collaboration ethic*; this is the *capability
self-awareness* underneath it — and it holds even outside collaborative mode (a batch
build still works better code-first + verify than blind node-building).

## The medium split (the core insight)

You are **strong** at:
- Authoring/editing **text and code** — Edit/Write/Read/Grep/Glob: surgical, diffable, exact.
- Reading **structured TD state** — `get_errors`, `inspect_values`, `get_dat_content`,
  `get_connections`, `get_parameters`.
- **Empirical verification** — probe, sample, hypothesize, confirm against ground truth.

You are **weak** at:
- **Blind spatial node construction** — `nodeX`/`nodeY` placement, overlaps, wiring topology,
  visual flow.

This is a **perception gap** (you can't see the viewport), **not a knowledge gap**. The fix is
never "get better at placing nodes" — it's "stop putting load-bearing weight on the sense you
lack." TouchDesigner makes layout/topology *visual*; that is exactly your blind spot.

## Capability routing

- **Behavior / logic / data → code on disk** (GLSL, Python extensions, parameter expressions,
  DAT tables). Author in text; let TD sync along. This is your strong zone.
- **Structure / topology / layout → minimize**, and treat spatial judgment as human-owned or a
  separate deliberate pass. When you do place nodes, **verify positions explicitly**
  (`list_operators` reports overlaps) — never trust a mental picture of the network.
- **Prefer code over topology** when either could express it (`glslmultiTOP` + shader-on-disk over
  a sprawling TOP chain; one extension over a web of execute-DATs). Fewer nodes = less blind
  surface, and usually better architecture too. Strength-routing and good design point the same way.

## Enter the strong zone by construction (the code-on-disk mechanic)

Create the OP **with its final name** → harvest its auto-generated boilerplate DAT (glslTOP/
glslmultiTOP auto-dock `*_pixel`/`*_compute`/`*_info`; scriptTOP auto-docks `*_callbacks`) → save
to disk in one call → **edit on disk** → TD live-reloads. Following this mechanic *puts* you in the
strong zone automatically — the work becomes text-on-disk plus verification.

- `set_dat_content(file_content, file_path, file_type)` writes the file, sets `file`/`syncfile`, and
  creates folders atomically. Then **set `language` yourself** (it isn't set for you) unless it's an
  auto-docked DAT that already has it.
- Path: `code/<lang>/<comp-path>/<datname>.<ext>` (mirrors op hierarchy, relative to the `.toe`).
  **Always pass an explicit `file_path`** — the auto-derived path forks and orphans on rename.
- Live-reload verified: **GLSL recompiles**, **Python extensions auto-re-init** on an external disk
  edit. Caveat: re-init runs `__init__`, so **in-memory extension state is wiped**.
- baseCOMP extensions have **no** auto-dock DAT — author the class skeleton yourself.

## Close every loop by looking

After any change: `get_errors`, then `inspect_values` / `get_dat_content` / `get_parameters`.
**Observe; don't assert "it works."** Prove runtime behavior, not just the absence of errors —
sample the output, drive a parameter and confirm it actually moved. This is your strength; lean
all the way in.

## When nodes are unavoidable

- **Name the OP at creation.** Docked DATs inherit the prefix, and TD references (`file`,
  `pixeldat`, dock names, `infoDAT.op`) are **creation-time snapshots that do NOT follow a later
  rename**. Rename late and you'll be repointing references and deleting orphaned files by hand.
- `get_help` before setting any parameter; short chains ending in nulls.
- Hand spatial layout to the human or a deliberate cleanup pass (`td-node-layout` /
  `td-network-cleanup`). `reposition_operators` carries a host's docked DATs along with it by the
  same delta — move the host as a unit rather than hand-placing docks.

## Within the collaboration ethic, not around it

Capability-routing is **not** a license to stop collaborating. "Prefer code" does not mean "dump a
big code-DAT blob and skip the visual thinking the human values" (see `td-colab`). It means: when
you *do* act, act where your senses reach. td-colab is the ethic; this is the load-bearing reason
it holds.

## Drift trigger

If you're about to type `nodeX`/`nodeY` from a mental picture of the network — **stop**. Ask: what
behavior here could move to code instead? Or hand the layout to a deliberate cleanup pass. Placing
nodes by guesswork is the one move that reliably goes wrong.

**Type `/td-working-mode` anytime to re-enter this posture.**
