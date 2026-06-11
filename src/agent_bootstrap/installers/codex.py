from __future__ import annotations


def codex_plan_action(kind: str, name: str, command: str) -> dict[str, str]:
    return {
        "agent": "codex",
        "kind": kind,
        "name": name,
        "mode": "plan-only",
        "suggested_command": command,
        "guardrail": "Do not execute without explicit user confirmation.",
    }
