from __future__ import annotations

from typing import Any

from .model import AuditResult, InstallPlan
from .policy import marketplace_decision


def build_install_plan(audit: AuditResult, marketplaces: list[dict[str, Any]]) -> InstallPlan:
    actions: list[dict[str, Any]] = []
    blocked_actions: list[dict[str, Any]] = []
    validation_steps: list[str] = list(audit.verification_commands)
    confirmation_required: list[str] = list(audit.confirmation_required)
    risk_summary: list[str] = list(audit.risks)

    for marketplace in marketplaces:
        agent = marketplace.get("agent", "generic")
        if agent not in {audit.agent, "generic"}:
            continue
        decision = marketplace_decision(marketplace)
        risk_summary.extend(decision["risks"])
        confirmation_required.extend(decision["confirmation"])
        validation_steps.extend(marketplace.get("validation_commands") or [])
        capabilities = marketplace.get("capabilities") or {}
        for capability_type in ("plugins", "skills", "mcp_servers"):
            for capability in capabilities.get(capability_type) or []:
                item_name = capability.get("name") if isinstance(capability, dict) else str(capability)
                action = {
                    "marketplace": marketplace.get("name", "unknown"),
                    "agent": agent,
                    "kind": capability_type.rstrip("s"),
                    "name": item_name,
                    "mode": "plan-install",
                    "suggested_command": capability.get("install_hint", "") if isinstance(capability, dict) else "",
                }
                if decision["can_plan"]:
                    actions.append(action)
                else:
                    action["blocked_reasons"] = decision["blocked"] or decision["risks"] or ["audit-only policy"]
                    blocked_actions.append(action)

    return InstallPlan(
        mode="plan-install",
        actions=actions,
        blocked_actions=blocked_actions,
        validation_steps=dedupe(validation_steps),
        confirmation_required=dedupe(confirmation_required),
        risk_summary=dedupe(risk_summary),
    )


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
