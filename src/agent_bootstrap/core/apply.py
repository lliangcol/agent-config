from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_bootstrap.core.evidence import CommandRunner, display_command
from agent_bootstrap.core.model import ApplyActionResult, ApplyResult
from agent_bootstrap.core.policy import load_yaml_file


CONFIRM_TOKEN = "EXECUTE_HOST_CHANGES"
ALLOWED_ACTION_TYPES = {"git_config", "powershell_execution_policy", "user_env"}
BLOCKED_ACTION_TYPES = {
    "package_install",
    "winget_install",
    "scoop_install",
    "apt_install",
    "curl_install",
    "agent_login",
    "agent_install",
    "plugin_install",
    "mcp_registration",
    "shell",
}
PLACEHOLDER_MARKERS = ("<", ">", "你的", "your ")


def apply_change_set(path: str | Path, runner: CommandRunner, confirm: str | None = None) -> ApplyResult:
    path = Path(path)
    data = load_yaml_file(path)
    if not isinstance(data, dict):
        raise ValueError(f"change set must be an object: {path}")
    actions = data.get("actions") or []
    if not isinstance(actions, list):
        raise ValueError(f"change set actions must be a list: {path}")

    dry_run = confirm != CONFIRM_TOKEN
    executed: list[ApplyActionResult] = []
    blocked: list[ApplyActionResult] = []
    skipped: list[ApplyActionResult] = []
    risks = [
        "apply can mutate user host configuration when confirmed; package installs, login flows, plugin installs, and MCP registration remain blocked."
    ]
    confirmation_required = [] if not dry_run else [f"Pass --confirm {CONFIRM_TOKEN} to execute allowlisted host configuration actions."]

    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            blocked.append(_result(str(index), "invalid", "Invalid action", "blocked", "", "action must be an object"))
            continue
        action_id = str(action.get("id") or f"action-{index + 1}")
        action_type = str(action.get("type") or "unknown")
        title = str(action.get("title") or action_id)

        if action_type in BLOCKED_ACTION_TYPES or action_type not in ALLOWED_ACTION_TYPES:
            blocked.append(
                _result(
                    action_id,
                    action_type,
                    title,
                    "blocked",
                    "",
                    f"action type {action_type} is not allowed for host execution",
                )
            )
            continue

        command, reason = _build_command(action_type, action, runner)
        command_text = display_command(command) if command else ""
        if reason:
            blocked.append(_result(action_id, action_type, title, "blocked", command_text, reason))
            continue

        if dry_run:
            skipped.append(_result(action_id, action_type, title, "dry-run", command_text, "confirmation token not supplied"))
            continue

        evidence = runner.run(command, timeout=int(action.get("timeout", 10)))
        status = "executed" if evidence.status == "ok" else "error"
        target = executed if evidence.status == "ok" else blocked
        target.append(
            ApplyActionResult(
                id=action_id,
                kind=action_type,
                title=title,
                status=status,
                command=command_text,
                reason=evidence.reason,
                evidence=evidence,
            )
        )

    return ApplyResult(
        mode="execute-after-confirm",
        dry_run=dry_run,
        change_set=str(path),
        executed=executed,
        blocked=blocked,
        skipped=skipped,
        confirmation_required=confirmation_required,
        risks=risks,
    )


def _build_command(action_type: str, action: dict[str, Any], runner: CommandRunner) -> tuple[list[str], str]:
    if action_type == "git_config":
        scope = str(action.get("scope") or "global")
        key = str(action.get("key") or "")
        value = str(action.get("value") or "")
        if scope != "global":
            return [], "only global git config is supported"
        if not key or not value:
            return [], "git_config requires key and value"
        if _has_placeholder(value):
            return [], "placeholder values must be replaced before execution"
        return ["git", "config", "--global", key, value], ""

    if action_type == "powershell_execution_policy":
        policy = str(action.get("policy") or "RemoteSigned")
        scope = str(action.get("scope") or "CurrentUser")
        if policy not in {"RemoteSigned", "Restricted", "AllSigned", "Bypass", "Unrestricted"}:
            return [], "unsupported PowerShell execution policy"
        if scope != "CurrentUser":
            return [], "only CurrentUser execution policy scope is supported"
        powershell = runner.which("pwsh") or runner.which("powershell")
        if powershell is None:
            return [], "PowerShell not found"
        return [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            f"Set-ExecutionPolicy -ExecutionPolicy {policy} -Scope {scope} -Force",
        ], ""

    if action_type == "user_env":
        name = str(action.get("name") or "")
        value = str(action.get("value") or "")
        if not name:
            return [], "user_env requires name"
        if _has_placeholder(value):
            return [], "placeholder values must be replaced before execution"
        return ["setx", name, value], ""

    return [], f"unsupported action type: {action_type}"


def _has_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def _result(action_id: str, kind: str, title: str, status: str, command: str, reason: str) -> ApplyActionResult:
    return ApplyActionResult(action_id, kind, title, status, command, reason)
