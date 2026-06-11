from __future__ import annotations


def environment_install_plan(tool_name: str, verify_command: str) -> dict[str, str]:
    return {
        "kind": "environment",
        "name": tool_name,
        "mode": "plan-only",
        "action": "Ask the user to confirm the preferred package manager and install path.",
        "verify_command": verify_command,
    }
