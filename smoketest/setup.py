#!/usr/bin/env python3
"""Generate a TDMCP smoke-test harness for an agent CLI.

Creates, in the given project directory:
- the host's instruction file (AGENTS.md / GEMINI.md / CLAUDE.md) with sandbox
  rules and the five smoke tests
- the host's MCP config for TDMCP (only if absent — never overwrites)
- per-test slash commands where the host supports project commands
- a project-local copy of the repo's td-* skills

The five test definitions live in TESTS below — the single source for both the
instruction file and the command files.

Usage:
    python smoketest/setup.py --host claude --project ../TestClaudeCodeWithMCP
    python smoketest/setup.py --host opencode --project ../TestOpenCodeWithMCP --lab opencode_lab
"""

import argparse
import json
import shutil
from pathlib import Path

# IPv4 loopback on purpose: the server binds 127.0.0.1, and `localhost`
# resolves to ::1 first on many hosts, which some clients report as refused.
MCP_URL = "http://127.0.0.1:13316/mcp"
REPO = Path(__file__).resolve().parent.parent

REPORT_LINE = (
    "Report: tools called, skills loaded, errors found, and the runtime values "
    "that prove the output works (not just absence of errors)."
)

# Each test: number, title, builder skills to load after td-general,
# mode line (extra rule, or None), and the test-specific steps.
TESTS = [
    {
        "n": 1,
        "title": "TOP chain with parameters and data table",
        "skills": ["td-top-family", "td-dat-family"],
        "mode": None,
        "steps": [
            "In /project1/{lab} build a TOP chain with build_network: "
            "noise_source → blur_soften → level_adjust → null_output. "
            "175px horizontal spacing, chain at Y=0.",
            "Set parameters (call get_help for all operator types first, in one "
            "batched call): noise_source resolution 512x512 and monochrome off; "
            "blur_soften sample step 7 in x and y; level_adjust input low 0.5.",
            "Create a tableDAT named table_data at the same X as noise_source, "
            "200px below the chain. Fill it with set_dat_content: heading row "
            "'pars | values', then rows 'seed | 4' and 'amp | 2'. The table is "
            "standalone data — do not wire or reference it.",
            "Verify: get_errors on /project1/{lab} is clean; inspect_values on "
            "null_output (sample_grid=8) shows non-monochrome noise; "
            "get_dat_content on table_data matches the spec exactly; "
            "get_parameters confirms every value set above.",
            "PASS requires: all five ops exist with the names above, every "
            "parameter and table cell verified at its specified value, zero errors.",
        ],
    },
    {
        "n": 2,
        "title": "CHOP-driven control",
        "skills": ["td-chop-family"],
        "mode": None,
        "steps": [
            "In /project1/{lab} create an lfoCHOP and use it to animate one "
            "parameter of a TOP (existing or new). Call get_help with NO pattern "
            "filter on the TOP type first and pick a real parameter name from the "
            "response. If a filtered lookup returns nothing, your guessed name is "
            "wrong — the parameter list, not the operator, is the truth.",
            "Verify: get_errors on /project1/{lab}, then inspect_values on the "
            "driven TOP twice a few seconds apart to confirm values change over time.",
        ],
    },
    {
        "n": 3,
        "title": "GLSL TOP",
        "skills": ["td-glsl-shaders"],
        "mode": None,
        "steps": [
            "In /project1/{lab} create a glslTOP with a simple pixel shader "
            "(e.g. animated gradient) in a docked text DAT. Set the DAT language "
            "to glsl. End the chain in a nullTOP.",
            "Verify: get_errors on /project1/{lab} — the shader must compile with "
            "zero errors — then inspect_values on the null.",
        ],
    },
    {
        "n": 4,
        "title": "Review broken network",
        "skills": ["td-review-network"],
        "mode": "REVIEW ONLY: never modify, fix, create, or delete any operator.",
        "steps": [
            "Find the intentionally broken network inside /project1/{lab} (if none "
            "exists, say so and stop). Use get_errors, get_connections, and "
            "get_parameters to trace every error to its root cause — trace "
            "upstream; the first broken op usually explains the rest.",
            "Report each error, its root cause, and the minimal fix you would "
            "make — but DO NOT make it.",
        ],
    },
    {
        "n": 5,
        "title": "Cleanup",
        "skills": ["td-network-cleanup", "td-node-layout"],
        "mode": "LAYOUT ONLY: only move, resize, color, and annotate — never create "
                "functional operators, change parameters, or delete anything.",
        "steps": [
            "Tidy /project1/{lab}: left-to-right flow, 175px horizontal / 125px "
            "vertical spacing, no overlapping operators (use reposition_operators "
            "for batch moves). Wrap each logical chain in an annotation describing it.",
            "Verify: list_operators on /project1/{lab} shows no overlaps; "
            "get_errors is clean.",
        ],
    },
]

HOSTS = {
    "claude": {
        "display": "Claude Code",
        "instructions": "CLAUDE.md",
        "skills_dir": ".claude/skills/",
        "command_dir": ".claude/commands",
        "command_format": "md",
        "mcp_file": ".mcp.json",
        "mcp_content": {"mcpServers": {"tdmcp": {"type": "http", "url": MCP_URL}}},
        "mcp_note": "Registered for this project in `.mcp.json` as the `tdmcp` MCP server.",
    },
    "codex": {
        "display": "Codex",
        "instructions": "AGENTS.md",
        "skills_dir": ".agents/skills/",
        "command_dir": None,  # Codex prompts are global-only (~/.codex/prompts)
        "command_format": None,
        "mcp_file": None,  # Codex MCP config is global
        "mcp_content": None,
        "mcp_note": "Registered globally in `~/.codex/config.toml`:\n"
                    "  [mcp_servers.touchdesigner]\n"
                    f"  url = \"{MCP_URL}\"",
    },
    "agy": {
        # Antigravity replaced the standalone Gemini CLI, which Google retired
        # on 2026-06-18. Skills mount from <workspace>/.agents/skills (probed);
        # MCP config is global, or carried by a plugin the user installs.
        "display": "Antigravity CLI",
        "instructions": "AGENTS.md",
        "skills_dir": ".agents/skills/",
        "command_dir": None,
        "command_format": None,
        "mcp_file": None,
        "mcp_content": None,
        "mcp_note": "Registered globally in `~/.gemini/config/mcp_config.json`:\n"
                    '  {"mcpServers": {"touchdesigner": {"serverUrl": '
                    f'"{MCP_URL}"}}}}}}\n'
                    "  (note serverUrl, not url — Antigravity rejects url)",
    },
    "opencode": {
        "display": "OpenCode",
        "instructions": "AGENTS.md",
        "skills_dir": ".agents/skills/",
        "command_dir": ".opencode/command",
        "command_format": "md",
        "mcp_file": "opencode.json",
        "mcp_content": {
            "$schema": "https://opencode.ai/config.json",
            "mcp": {"tdmcp": {"type": "remote", "url": MCP_URL, "enabled": True}},
        },
        "mcp_note": "Registered for this project in `opencode.json` as the `tdmcp` MCP server.",
    },
}


def test_steps(test, lab):
    """Full numbered step list for one test, skill loading included."""
    steps = ["Load the skill `td-general` and follow its conventions (operator "
             "naming: optype_purpose, e.g. noise_source not noise1; get_help "
             "before setting any parameter)."]
    for skill in test["skills"]:
        steps.append(f"Load the skill `{skill}`.")
    steps.extend(s.format(lab=lab) for s in test["steps"])
    steps.append(REPORT_LINE)
    return steps


def render_test_block(test, lab):
    lines = [f"### Smoke test {test['n']} — {test['title']}", ""]
    if test["mode"]:
        lines.append(f"**{test['mode']}**")
        lines.append("")
    lines.extend(f"{i}. {s}" for i, s in enumerate(test_steps(test, lab), 1))
    return "\n".join(lines)


def render_instructions(host, project_name, lab):
    h = HOSTS[host]
    tests = "\n\n".join(render_test_block(t, lab) for t in TESTS)
    return f"""# {project_name} — TDMCP smoke-test harness for {h['display']}

This project tests {h['display']}'s ability to drive a **live TouchDesigner session**
through the TDMCP MCP server. Other agents may be working in the **same TouchDesigner
session at the same time** — strict sandbox rules below.

## Sandbox — collision rules (non-negotiable)

- Your assigned sandbox is the COMP **`/project1/{lab}`** in the live session.
- Do ALL work inside `/project1/{lab}`. Never create, edit, move, or delete
  operators anywhere else in the project.
- Other `*_lab` COMPs under `/project1` belong to other agents — never enter or
  modify them.
- If `/project1/{lab}` does not exist, create it as a `baseCOMP`, then work inside it.
- Never call `save_project` unless the user explicitly asks.

## MCP connection

- TDMCP serves MCP over HTTP at `{MCP_URL}`.
- {h['mcp_note']}
- TouchDesigner must be running with TDMCP started. If tools cannot connect,
  report that and stop — do not retry endlessly.

## Skills

- TouchDesigner workflow skills are installed project-locally in `{h['skills_dir']}`.
- **Step zero of EVERY smoke test: load the `td-general` skill** — before any
  builder skill, before any MCP call. It holds the naming convention
  (`optype_purpose`, e.g. `noise_source` not `noise1`), the get-help-first rule,
  and tells you which builder skill to load for each operator family.
- Then load the relevant builder skill for the task.
- Follow the workflow: Scout → Plan → Build → Review → Cleanup.

## Smoke tests

Run whichever the user asks for, entirely inside `/project1/{lab}`. Start each
test in a fresh session/context for comparable results.

{tests}
"""


def render_command(test, lab, fmt):
    desc = f"Smoke test {test['n']} — {test['title']} in /project1/{lab}"
    rules = [
        f"Work ONLY inside /project1/{lab}. Never create, edit, or delete "
        "operators anywhere else.",
        "Never call save_project.",
    ]
    if test["mode"]:
        rules.insert(0, test["mode"])
    body_lines = ["Smoke-test TouchDesigner via the tdmcp MCP tools.", "",
                  "RULES (non-negotiable):"]
    body_lines.extend(f"- {r}" for r in rules)
    body_lines.extend(["", "Steps, in order:"])
    body_lines.extend(f"{i}. {s}" for i, s in enumerate(test_steps(test, lab), 1))
    body = "\n".join(body_lines)

    if fmt == "md":
        return f"---\ndescription: {desc}\n---\n{body}\n"
    if fmt == "toml":
        return f'description = "{desc}"\nprompt = """\n{body}\n"""\n'
    raise ValueError(fmt)


def write_if_absent(path, content, label):
    if path.exists():
        print(f"  {label}: exists, left untouched ({path})")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  {label}: wrote {path}")


def copy_skills(dest):
    """Copy this repo's td-* skills into dest.

    install.py used to do this. It was removed when TDMCPSkills became a content
    repo — installation lives in the TDMCP component now. The harness only needs
    a plain copy into a known directory, with no manifest and no pruning, and it
    must work without TouchDesigner running, so it does the copy itself rather
    than driving the component.
    """
    src = REPO / "skills"
    names = sorted(d.name for d in src.iterdir()
                   if d.is_dir() and d.name.startswith("td-")
                   and (d / "SKILL.md").is_file())
    dest.mkdir(parents=True, exist_ok=True)
    for n in names:
        target = dest / n
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(src / n, target)
    print(f"  skills: copied {len(names)} into {dest}")


def main():
    parser = argparse.ArgumentParser(description="Generate a TDMCP smoke-test harness")
    parser.add_argument("--host", required=True, choices=sorted(HOSTS))
    parser.add_argument("--project", required=True, metavar="PATH")
    parser.add_argument("--lab", help="Sandbox COMP name (default: <host>_lab)")
    parser.add_argument("--skip-install", action="store_true",
                        help="Skip the project-local skill install")
    args = parser.parse_args()

    h = HOSTS[args.host]
    project = Path(args.project).resolve()
    project.mkdir(parents=True, exist_ok=True)
    lab = args.lab or f"{args.host}_lab"

    print(f"Harness for {h['display']} in {project} (sandbox: /project1/{lab})")

    # Instruction file — always (re)written: it is generated, not hand-edited
    inst = project / h["instructions"]
    inst.write_text(render_instructions(args.host, project.name, lab), encoding="utf-8")
    print(f"  instructions: wrote {inst}")

    # MCP config — never overwrite an existing one
    if h["mcp_file"]:
        write_if_absent(project / h["mcp_file"],
                        json.dumps(h["mcp_content"], indent=2) + "\n", "mcp config")
    else:
        print(f"  mcp config: global for {h['display']} — ensure:\n    {h['mcp_note']}")

    # Per-test commands — regenerated alongside the instruction file
    if h["command_dir"]:
        cmd_dir = project / h["command_dir"]
        cmd_dir.mkdir(parents=True, exist_ok=True)
        ext = h["command_format"]
        for t in TESTS:
            (cmd_dir / f"smoketest{t['n']}.{ext}").write_text(
                render_command(t, lab, ext), encoding="utf-8")
        print(f"  commands: wrote smoketest1-{len(TESTS)} in {cmd_dir}")

    if not args.skip_install:
        copy_skills(project / h["skills_dir"])

    print(f"Done. Start {h['display']} in {project} and run smoke test 1.")


if __name__ == "__main__":
    main()
