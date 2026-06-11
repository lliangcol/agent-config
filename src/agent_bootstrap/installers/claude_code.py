from __future__ import annotations


def claude_code_plan_action(kind: str, name: str, command: str) -> dict[str, str]:
    return {
        "agent": "claude-code",
        "kind": kind,
        "name": name,
        "mode": "plan-only",
        "suggested_command": command,
        "guardrail": "Do not execute without explicit user confirmation; run /reload-plugins only after confirmed plugin changes.",
    }
