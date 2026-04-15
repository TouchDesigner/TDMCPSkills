---
description: Analyze session tool usage and audit skills for consistency, efficiency, and redundancy. Use after builds to review what happened and improve the skill system, or when skills feel stale or contradictory.
user_invocable: true
---

# Learn

Analyzes how tools were used during the session and audits the skill system. Combines runtime log analysis with skill file quality checks to propose concrete improvements.

## When to Run

- After a build session — to review tool usage patterns and update skills
- When a skill's instructions led to a wrong outcome
- When the user wants to review/optimize the workflow
- Periodically to keep skills tight and efficient

## Process

### 1. Analyze Session Logs

Run the analyzer: `python skills/td-learn/scripts/analyzer.py`

The analyzer reads the current session's JSONL log from `.claude/analytics/sessions/` and reports:
- **Tool call frequency** — which tools were called and how often
- **Repeated calls** — same tool + same target called multiple times (candidates for batching or caching)
- **Sequential pairs** — tool A always followed by tool B (candidates for merging or skill instruction updates)
- **High-output calls** — tools returning large responses (candidates for filtering with `names`/`pattern`)
- **execute_code usage** — flags cases where a dedicated tool exists
- **Agent vs main** — how much work was done by subagents vs main conversation
- **Per-skill breakdown** — if skills were loaded, groups tool calls by active skill

Review the report. Connect patterns to skill improvements:
- Repeated `get_help` calls → skill is missing par names, add them
- Repeated `get_parameters` on same operator → skill should instruct to batch or cache
- `execute_code` where dedicated tool exists → skill should prefer the dedicated tool
- High-output calls without filters → skill should instruct to use `names`/`pattern`

### 2. Review Conversation Context

Beyond the logs, review the current conversation:
- What was built, which skills were loaded
- What went well, what failed
- Any MCP tool call failures — classify as:
  - **Argument parsing** — complex params arrived as strings. Check `_coerce_arguments` or add `json.loads` fallback
  - **Type coercion** — integers arrived as floats. Check handlers cast with `int()`
  - **Missing error context** — cryptic error. Improve handler message
  - **Schema mismatch** — wrong parameter names/types. Improve schema description

### 3. Classify Issues

- **Missing knowledge** — skill didn't cover a parameter or pattern → add to the right skill
- **Wrong skill** — task loaded wrong skill → update descriptions/triggers
- **Redundancy** — same rule in two skills → keep in one, reference from other
- **Incorrect instruction** — skill caused wrong result → fix the instruction
- **Missing rule** — no guidance for a situation that came up → add to appropriate skill
- **Contradiction** — two skills disagree → resolve, single source of truth
- **Tool misuse** — execute_code where dedicated tool exists → update skill to prefer dedicated tool

### 4. Prioritize

- **Blocking** — caused a build failure or wrong output → fix immediately
- **Frequent** — came up multiple times or across sessions → fix soon
- **Efficiency** — wasted tokens or steps but didn't break anything → fix when convenient
- **Nice-to-have** — minor improvement, no observed problem → defer

### 5. Audit Each Touched Skill

For every skill that was loaded or should have been loaded:

- **Read the SKILL.md** in full
- **Consistency** — does it contradict CLAUDE.md, other skills, or itself?
- **Redundancy** — does it duplicate content from another skill?
- **Completeness** — was something missing that caused a problem?
- **Efficiency** — could it be shorter without losing information?
- **Hierarchy** — does it reference cross-cutting skills (td-node-layout, etc.) instead of inlining their rules?

### 6. Check Hierarchy

The skill system is layered: `CLAUDE.md` (always loaded) → `SKILLS.md` (loaded before builds) → individual skills (loaded per task).

Rules for where information lives:
- **CLAUDE.md** — only workflow steps and guardrails. No domain knowledge
- **Cross-cutting skills** (td-node-layout, td-performance-check) — conventions shared across builders. Each builder references these, never duplicates them
- **Builder skills** — domain-specific knowledge. Reference cross-cutting skills, don't inline them
- **Workflow skills** — phase-specific process (td-build-planning, td-review-network, td-network-cleanup, td-learn)

### 7. Propose Changes

For each issue found, propose a specific fix:
- **Move** — content in the wrong skill → name source and destination
- **Deduplicate** — same content in two places → keep in one, reference from other
- **Add** — missing knowledge that caused a problem → write it, place it in the right skill
- **Remove** — content that's never useful or derivable from code → delete it
- **Shorten** — verbose content → tighten without losing meaning

Present proposals to the user before making changes.

### 8. Apply

After user approval:
- Edit the affected SKILL.md files
- Update SKILLS.md index if skills were added/removed/recategorized
- Update CLAUDE.md only if workflow or guardrails changed

### 9. Audit Memory for Skill-Worthy Knowledge

Scan memory files (MEMORY.md index) for TD-specific knowledge that should live in skills instead. Memory is personal context — TD knowledge belongs in skills.

- **TD patterns/conventions** in memory → move to the appropriate skill
- **Tool behavior** (parameter names, gotchas) → move to relevant skill or CLAUDE.md
- **User preferences** (workflow style, feedback) → keep in memory
- **Project context** (deadlines, team info) → keep in memory

After moving TD knowledge to skills, remove the redundant memory entry or update it to reference the skill instead.

### 10. Compactness Audit

Run across **all** skills (not just touched ones):

- **No tables** — convert to bullet lists
- **No prose** — remove filler words, explanations of obvious things
- **Terse bullets** — state the rule, not the rationale. One concept per line
- **No redundant examples** — one example per pattern is enough
- **Bullet lists only** — parameter lists, patterns, pitfalls all as `- **name** — description`
- **"Would the agent get this wrong?"** — if no, cut it
- **Flag bloat** — if a skill exceeds ~80 lines or ~4,000 tokens, check for content that can be shortened or moved to `references/`
- **Check CLAUDE.md** — same rules apply, keep it tight

### 11. Best Practices Audit

- **Defaults over menus** — pick a clear default, mention alternatives briefly. Flag equal-option lists without a recommendation
- **Specificity matches fragility** — prescriptive for fragile operations, flexible for creative decisions
- **Progressive disclosure** — dense skills should move deep reference to `references/` with load triggers
- **Scope coherence** — each skill covers a coherent unit of work. Flag too-narrow or too-broad skills
- **Description quality** — check trigger descriptions are accurate and don't overlap other skills
- **Procedures over declarations** — teach *how to approach* problems, not *what to produce*

### 12. Report Stats

End every run with: `python skills/td-learn/scripts/skill_stats.py`

Reports lines and estimated tokens per skill, sorted by token count. Flags skills over the ~80 line / ~4,000 token budget.

## What NOT to Optimize

- Don't restructure for the sake of restructuring — only fix actual problems
- Don't add speculative content for hypothetical future needs
- Don't merge skills that serve different purposes just because they're short
- Don't split a skill unless it's clearly serving two unrelated audiences
- No ASCII art or tree diagrams in skill files
