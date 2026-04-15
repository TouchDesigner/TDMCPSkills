#!/usr/bin/env python3
"""Analyze session JSONL logs for tool usage patterns and inefficiencies.

Reads the most recent (or specified) session log and reports:
- Tool call frequency and estimated token flow
- Repeated calls to the same tool with same target
- Sequential tool pairs that always appear together
- High-output calls that could use filtering
- execute_code usage where dedicated tools exist
- Per-agent breakdown (main vs subagents)
"""

import json
import sys
import os
from collections import Counter, defaultdict
from pathlib import Path

CHARS_PER_TOKEN = 4

# Tools that have dedicated alternatives to execute_code
DEDICATED_TOOLS = {
    "create_operator": "creating operators",
    "build_network": "creating multiple operators",
    "edit_operator": "delete, rename, copy, reposition, flags, color",
    "parameters": "setting parameter values (with values arg)",
    "wiring": "connecting/disconnecting operators",
}


def load_session(log_path):
    """Load all entries from a JSONL session file."""
    entries = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def find_latest_session(analytics_dir):
    """Find the most recently modified session file."""
    session_dir = analytics_dir / "sessions"
    if not session_dir.exists():
        return None
    files = sorted(session_dir.glob("session_*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)
    return files[0] if files else None


def find_current_session(analytics_dir, session_id=None):
    """Find session file by ID or fall back to latest."""
    session_dir = analytics_dir / "sessions"
    if session_id:
        target = session_dir / f"session_{session_id}.jsonl"
        if target.exists():
            return target
    return find_latest_session(analytics_dir)


def get_tool_target(entry):
    """Extract the primary target identifier from a tool call's params."""
    params = entry.get("params", {})
    tool = entry.get("tool", "")

    # MCP tools — path is the main target
    for key in ("path", "operator_path", "file_path"):
        if key in params:
            return params[key]

    # operator_type for create calls
    if "operator_type" in params:
        return params["operator_type"]

    # pattern for search/glob
    if "pattern" in params:
        return params["pattern"]

    # command for Bash
    if "command" in params:
        cmd = params["command"]
        return cmd[:80] if len(cmd) > 80 else cmd

    return None


def analyze_frequency(entries):
    """Count tool call frequency and estimate token flow."""
    tool_calls = [e for e in entries if e.get("event") != "SessionStart" and e.get("tool")]
    freq = Counter(e["tool"] for e in tool_calls)

    # Estimate tokens from output_chars
    token_flow = defaultdict(int)
    for e in tool_calls:
        chars = e.get("output_chars") or 0
        token_flow[e["tool"]] += chars // CHARS_PER_TOKEN

    return freq, token_flow


def find_repeated_calls(entries):
    """Find cases where same tool + same target was called multiple times."""
    tool_calls = [e for e in entries if e.get("tool")]
    seen = defaultdict(int)
    for e in tool_calls:
        target = get_tool_target(e)
        if target:
            key = (e["tool"], target)
            seen[key] += 1
    return {k: v for k, v in seen.items() if v > 1}


def find_sequential_pairs(entries):
    """Find tool pairs that frequently appear in sequence."""
    tool_calls = [e for e in entries if e.get("tool")]
    pairs = Counter()
    for i in range(len(tool_calls) - 1):
        a = tool_calls[i]["tool"]
        b = tool_calls[i + 1]["tool"]
        pairs[(a, b)] += 1
    return {k: v for k, v in pairs.items() if v >= 2}


def find_high_output(entries, threshold=4000):
    """Find tool calls with large output (estimated tokens > threshold)."""
    results = []
    for e in entries:
        chars = e.get("output_chars") or 0
        tokens = chars // CHARS_PER_TOKEN
        if tokens > threshold:
            results.append({
                "tool": e.get("tool"),
                "target": get_tool_target(e),
                "est_tokens": tokens,
                "params": e.get("params", {}),
            })
    return results


def find_execute_code_misuse(entries):
    """Flag execute_code calls that could use dedicated tools."""
    flags = []
    for e in entries:
        if e.get("tool") in ("mcp__touchdesigner__execute_code", "execute_code"):
            params = e.get("params", {})
            code = params.get("code", "")
            for tool_name, purpose in DEDICATED_TOOLS.items():
                # Simple heuristic checks
                if tool_name == "create_operator" and ("create(" in code or ".create(" in code):
                    flags.append({"code_snippet": code[:100], "suggested_tool": tool_name, "purpose": purpose})
                elif tool_name == "wiring" and (".inputConnectors" in code or ".outputConnectors" in code):
                    flags.append({"code_snippet": code[:100], "suggested_tool": tool_name, "purpose": purpose})
                elif tool_name == "parameters" and (".par." in code and "=" in code):
                    flags.append({"code_snippet": code[:100], "suggested_tool": tool_name, "purpose": purpose})
    return flags


def analyze_agents(entries):
    """Break down tool calls by agent (main vs subagents)."""
    main_calls = 0
    agent_calls = defaultdict(int)
    for e in entries:
        if not e.get("tool"):
            continue
        agent_id = e.get("agent_id")
        if agent_id:
            agent_type = e.get("agent_type", "unknown")
            agent_calls[f"{agent_type} ({agent_id[:8]})"] += 1
        else:
            main_calls += 1
    return main_calls, dict(agent_calls)


def format_report(entries, log_path):
    """Generate the full analysis report."""
    lines = []
    lines.append(f"## Session Analysis: {log_path.name}")
    lines.append(f"- **Total events**: {len(entries)}")

    tool_calls = [e for e in entries if e.get("tool")]
    lines.append(f"- **Tool calls**: {len(tool_calls)}")

    if not tool_calls:
        lines.append("\nNo tool calls to analyze.")
        return "\n".join(lines)

    # Duration
    timestamps = [e["ts"] for e in entries if "ts" in e]
    if len(timestamps) >= 2:
        duration_min = (max(timestamps) - min(timestamps)) / 60
        lines.append(f"- **Session duration**: {duration_min:.1f} min")

    # Frequency
    freq, token_flow = analyze_frequency(entries)
    lines.append("\n### Tool Call Frequency")
    lines.append(f"{'Tool':<45} {'Calls':>6} {'Est Tokens':>10}")
    lines.append(f"{'-'*45} {'-'*6} {'-'*10}")
    for tool, count in freq.most_common():
        tokens = token_flow.get(tool, 0)
        short_name = tool.replace("mcp__touchdesigner__", "td:")
        lines.append(f"{short_name:<45} {count:>6} {tokens:>10}")
    total_tokens = sum(token_flow.values())
    lines.append(f"{'TOTAL':<45} {sum(freq.values()):>6} {total_tokens:>10}")

    # Repeated calls
    repeated = find_repeated_calls(entries)
    if repeated:
        lines.append("\n### Repeated Calls (same tool + target)")
        for (tool, target), count in sorted(repeated.items(), key=lambda x: -x[1]):
            short_tool = tool.replace("mcp__touchdesigner__", "td:")
            short_target = target[:60] if len(target) > 60 else target
            lines.append(f"- **{short_tool}** on `{short_target}` x{count}")

    # Sequential pairs
    pairs = find_sequential_pairs(entries)
    if pairs:
        lines.append("\n### Frequent Sequential Pairs")
        for (a, b), count in sorted(pairs.items(), key=lambda x: -x[1]):
            short_a = a.replace("mcp__touchdesigner__", "td:")
            short_b = b.replace("mcp__touchdesigner__", "td:")
            lines.append(f"- **{short_a}** → **{short_b}** x{count}")

    # High output
    high = find_high_output(entries)
    if high:
        lines.append("\n### High-Output Calls (>4000 est tokens)")
        for h in sorted(high, key=lambda x: -x["est_tokens"]):
            short_tool = h["tool"].replace("mcp__touchdesigner__", "td:")
            target = h["target"] or "?"
            lines.append(f"- **{short_tool}** on `{target}` — ~{h['est_tokens']} tokens")

    # execute_code misuse
    misuse = find_execute_code_misuse(entries)
    if misuse:
        lines.append("\n### execute_code Misuse")
        for m in misuse:
            lines.append(f"- Could use **{m['suggested_tool']}** ({m['purpose']}): `{m['code_snippet']}`")

    # Agent breakdown
    main_count, agent_counts = analyze_agents(entries)
    if agent_counts:
        lines.append("\n### Agent Breakdown")
        lines.append(f"- **Main conversation**: {main_count} calls")
        for agent, count in sorted(agent_counts.items(), key=lambda x: -x[1]):
            lines.append(f"- **{agent}**: {count} calls")

    return "\n".join(lines)


def main():
    root = Path(__file__).resolve().parents[3]  # scripts -> learn -> skills -> repo root
    analytics_dir = root / ".claude" / "analytics"

    # Accept optional session_id as argument
    session_id = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SESSION_ID")

    log_path = find_current_session(analytics_dir, session_id)
    if not log_path:
        print("No session logs found in .claude/analytics/sessions/")
        print("Hooks may not be configured yet. Check .claude/settings.local.json")
        sys.exit(1)

    entries = load_session(log_path)
    if not entries:
        print(f"Session log {log_path.name} is empty — no tool calls recorded yet.")
        sys.exit(0)

    report = format_report(entries, log_path)
    print(report)


if __name__ == "__main__":
    main()
