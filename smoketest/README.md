# TDMCP Smoke Tests

A reproducible harness for testing any supported agent CLI against a live
TouchDesigner session via TDMCP. Used to verify that skills are discovered,
loaded in the right order, and followed — across Claude Code, Codex, Gemini CLI,
and OpenCode, including small local models.

## The five tests

1. **TOP chain** — noise → blur → level → null, verified with runtime values
2. **CHOP-driven control** — lfoCHOP animating a TOP parameter
3. **GLSL TOP** — pixel shader that must compile clean
4. **Review broken network** — diagnose root cause, review only (requires a
   deliberately broken network planted in the lab first)
5. **Cleanup** — layout, spacing, annotations only

Definitions live in `setup.py` (`TESTS`) — the single source for the generated
instruction files and slash commands.

## Setup

Prerequisites: TouchDesigner running with TDMCP started (`http://localhost:13316/mcp`).

Generate a harness folder per host:

```bash
python smoketest/setup.py --host claude   --project ../TestClaudeCodeWithMCP
python smoketest/setup.py --host codex    --project ../TestCodexWithMCP
python smoketest/setup.py --host gemini   --project ../TestGeminiWithMCP
python smoketest/setup.py --host opencode --project ../TestOpenCodeWithMCP
```

Each run writes the host's instruction file (`AGENTS.md` / `GEMINI.md` /
`CLAUDE.md`), the host's TDMCP MCP config (only if absent — an existing config
is never overwritten), per-test slash commands where the host supports project
commands, and a project-local skill install.

## Isolation model

Every host gets its own sandbox COMP under `/project1` (`claude_lab`,
`codex_lab`, ...). Agents are instructed to work only inside their own lab and
to create it if missing, so multiple agents can run against the same
TouchDesigner session concurrently without colliding. Override the name with
`--lab`.

## Running

Start the agent CLI inside its harness folder and run one test per fresh
session (`/new` or restart) so results are comparable and context never leaks
between tests:

- Hosts with project commands (Claude Code, Gemini CLI, OpenCode): `/smoketest1` … `/smoketest5`
- Codex: ask `run smoke test 1` — it follows `AGENTS.md`

A pass requires: correct skills loaded (td-general first), conventions followed
(`optype_purpose` naming, get_help before set_parameters), zero errors, and
verification with runtime values — not just absence of errors.

## Notes

- Small/local models (e.g. qwen3:14b via OpenCode + Ollama) ignore instruction
  files in fresh sessions — use the generated slash commands, which carry the
  full rules in the prompt.
- Test 4 needs an intentionally broken network planted in each lab beforehand;
  the test instructs the agent to stop if none exists.
- Instruction and command files are generated — edit `setup.py` and re-run,
  don't hand-edit the output.
