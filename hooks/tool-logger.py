#!/usr/bin/env python3
"""Claude Code hook that logs tool calls to per-session JSONL files.

Receives JSON on stdin from PostToolUse / SessionStart hooks.
Writes one JSON line per event to .claude/analytics/sessions/session_{id}.jsonl
"""

import json
import sys
import time
from pathlib import Path

# Truncate param values longer than this
MAX_PARAM_VALUE_LEN = 200

# Keys whose values are typically large blobs (code, content) — truncate aggressively
BLOB_KEYS = {"code", "content", "text", "new_string", "old_string", "body", "pixel_dat_content", "command"}

# Keys that identify *what* was targeted — always keep full
IDENTITY_KEYS = {"path", "operator_type", "names", "pattern", "name", "tool_name", "file_path", "operator_path"}


def truncate_value(value, max_len=MAX_PARAM_VALUE_LEN):
    """Truncate a string value, preserving the start."""
    if not isinstance(value, str):
        value = json.dumps(value)
    if len(value) <= max_len:
        return value
    return value[:max_len] + f"...({len(value)} chars)"


def truncate_params(params):
    """Truncate tool_input params for logging. Keep identity keys full, truncate blobs."""
    if not isinstance(params, dict):
        return params
    result = {}
    for key, value in params.items():
        if key in IDENTITY_KEYS:
            result[key] = value if isinstance(value, str) and len(value) <= MAX_PARAM_VALUE_LEN * 2 else truncate_value(value, MAX_PARAM_VALUE_LEN * 2)
        elif key in BLOB_KEYS:
            result[key] = truncate_value(value, 100)
        elif isinstance(value, dict):
            result[key] = truncate_params(value)
        elif isinstance(value, list):
            result[key] = value[:5] if len(value) > 5 else value
        else:
            result[key] = truncate_value(value)
    return result


def get_output_chars(data):
    """Estimate output size from tool_response if present."""
    output = data.get("tool_response")
    if output is None:
        return None
    if isinstance(output, str):
        return len(output)
    return len(json.dumps(output))


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    session_id = data.get("session_id", "unknown")
    event_name = data.get("hook_event_name", "unknown")

    # Resolve analytics dir relative to this script's location
    script_dir = Path(__file__).resolve().parent
    analytics_dir = script_dir.parent / "analytics" / "sessions"
    analytics_dir.mkdir(parents=True, exist_ok=True)

    log_file = analytics_dir / f"session_{session_id}.jsonl"

    entry = {
        "ts": time.time(),
        "event": event_name,
        "session_id": session_id,
    }

    if event_name == "SessionStart":
        entry["type"] = "session_start"
        entry["cwd"] = data.get("cwd")
    else:
        # Tool call event
        entry["tool"] = data.get("tool_name")
        entry["agent_id"] = data.get("agent_id")
        entry["agent_type"] = data.get("agent_type")
        entry["params"] = truncate_params(data.get("tool_input", {}))
        entry["output_chars"] = get_output_chars(data)
        if data.get("execution_duration_ms") is not None:
            entry["duration_ms"] = data.get("execution_duration_ms")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
