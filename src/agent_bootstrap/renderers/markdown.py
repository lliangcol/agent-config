from __future__ import annotations

from agent_bootstrap.core.model import ApplyResult, AuditResult, CapabilityFinding, Evidence, InstallPlan


def render_audit_markdown(audit: AuditResult) -> str:
    lines = [
        "# Agent Capability Bootstrap Audit",
        "",
        "## Environment",
        f"- OS: {audit.os}",
        f"- Shell: {audit.shell}",
        f"- Architecture: {audit.arch}",
        f"- Agent: {audit.agent}",
        "",
        "## Core Tools",
    ]
    lines.extend(_finding_lines(audit.tools.values()))
    lines.append("")
    lines.append("## Package Managers")
    lines.extend(_finding_lines(audit.package_managers.values()))
    lines.append("")
    if audit.capabilities:
        lines.append("## Capability Groups")
        for group_name in sorted(audit.capabilities):
            lines.append(f"### {group_name}")
            lines.extend(_finding_lines(audit.capabilities[group_name]) or ["- None"])
            lines.append("")
    lines.append("## Network")
    lines.extend(_evidence_lines(audit.network))
    lines.append("")
    lines.append("## Agent Config Paths")
    lines.extend(_evidence_lines(audit.config_paths) or ["- None inspected"])
    lines.append("")
    lines.append("## Installed Summary")
    lines.extend(_summary_lines(audit.installed_summary))
    lines.append("")
    lines.append("## Missing Items")
    lines.extend(_finding_lines(audit.missing) or ["- None"])
    lines.append("")
    lines.append("## Recommended Items")
    lines.extend(_finding_lines(audit.recommended) or ["- None"])
    lines.append("")
    lines.append("## Risks")
    lines.extend([f"- {item}" for item in audit.risks] or ["- None"])
    lines.append("")
    lines.append("## Needs Confirmation")
    lines.extend([f"- {item}" for item in audit.confirmation_required] or ["- None"])
    lines.append("")
    lines.append("## Verification Commands")
    lines.extend([f"- `{item}`" for item in audit.verification_commands] or ["- None"])
    lines.append("")
    return "\n".join(lines)


def render_plan_markdown(plan: InstallPlan) -> str:
    lines = [
        "# Agent Capability Install Plan",
        "",
        f"- Mode: {plan.mode}",
        "",
        "## Planned Actions",
    ]
    lines.extend(_action_lines(plan.actions) or ["- None"])
    lines.append("")
    lines.append("## Blocked Actions")
    lines.extend(_action_lines(plan.blocked_actions) or ["- None"])
    lines.append("")
    lines.append("## Needs Confirmation")
    lines.extend([f"- {item}" for item in plan.confirmation_required] or ["- None"])
    lines.append("")
    lines.append("## Risk Summary")
    lines.extend([f"- {item}" for item in plan.risk_summary] or ["- None"])
    lines.append("")
    lines.append("## Validation Steps")
    lines.extend([f"- `{item}`" for item in plan.validation_steps] or ["- None"])
    lines.append("")
    return "\n".join(lines)


def render_apply_markdown(result: ApplyResult) -> str:
    lines = [
        "# Agent Capability Apply Result",
        "",
        f"- Mode: {result.mode}",
        f"- Dry run: {str(result.dry_run).lower()}",
        f"- Change set: {result.change_set}",
        "",
        "## Executed Actions",
    ]
    lines.extend(_apply_action_lines(result.executed) or ["- None"])
    lines.append("")
    lines.append("## Blocked Actions")
    lines.extend(_apply_action_lines(result.blocked) or ["- None"])
    lines.append("")
    lines.append("## Skipped Actions")
    lines.extend(_apply_action_lines(result.skipped) or ["- None"])
    lines.append("")
    lines.append("## Needs Confirmation")
    lines.extend([f"- {item}" for item in result.confirmation_required] or ["- None"])
    lines.append("")
    lines.append("## Risks")
    lines.extend([f"- {item}" for item in result.risks] or ["- None"])
    lines.append("")
    return "\n".join(lines)


def _finding_lines(findings) -> list[str]:
    lines: list[str] = []
    for finding in findings:
        status = "present" if finding.present else "missing"
        lines.append(f"- {finding.name} ({finding.kind}): {status}, risk={finding.risk}")
        if finding.recommendation:
            lines.append(f"  - Recommendation: {finding.recommendation}")
        for evidence in finding.evidence:
            lines.append(f"  - Evidence: `{evidence.command}` -> {evidence.status}; {evidence.reason}; value={evidence.value}")
    return lines


def _evidence_lines(items: list[Evidence]) -> list[str]:
    return [f"- `{item.command}` -> {item.status}; {item.reason}; value={item.value}" for item in items]


def _summary_lines(summary: dict) -> list[str]:
    lines: list[str] = []
    for key in sorted(summary):
        value = summary[key]
        if isinstance(value, list):
            lines.append(f"- {key}: {len(value)} entries")
        else:
            lines.append(f"- {key}: {value}")
    return lines


def _action_lines(actions: list[dict]) -> list[str]:
    lines: list[str] = []
    for action in actions:
        name = action.get("name", "unknown")
        kind = action.get("kind", "unknown")
        marketplace = action.get("marketplace", "unknown")
        command = action.get("suggested_command", "")
        lines.append(f"- {kind}: {name} from {marketplace}")
        if command:
            lines.append(f"  - Suggested command: `{command}`")
        if action.get("blocked_reasons"):
            lines.append("  - Blocked: " + "; ".join(action["blocked_reasons"]))
    return lines


def _apply_action_lines(actions) -> list[str]:
    lines: list[str] = []
    for action in actions:
        lines.append(f"- {action.id} ({action.kind}): {action.status}; {action.title}")
        if action.command:
            lines.append(f"  - Command: `{action.command}`")
        if action.reason:
            lines.append(f"  - Reason: {action.reason}")
        if action.evidence:
            lines.append(
                f"  - Evidence: `{action.evidence.command}` -> {action.evidence.status}; "
                f"{action.evidence.reason}; value={action.evidence.value}"
            )
    return lines
