from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from agent_bootstrap.adapters.base import AdapterContext, select_agent_name
from agent_bootstrap.adapters.claude_code import ClaudeCodeAdapter
from agent_bootstrap.adapters.codex import CodexAdapter
from agent_bootstrap.adapters.generic import GenericAdapter
from agent_bootstrap.core.apply import apply_change_set
from agent_bootstrap.core.evidence import CommandRunner
from agent_bootstrap.core.model import AuditResult, CapabilityFinding
from agent_bootstrap.core.planner import build_install_plan
from agent_bootstrap.core.policy import load_profile
from agent_bootstrap.detectors.os_env import detect_os_shell_arch, path_entries
from agent_bootstrap.detectors.package_managers import detect_package_managers
from agent_bootstrap.detectors.runtimes import detect_core_tools, detect_network
from agent_bootstrap.detectors.workstation import detect_workstation_capabilities
from agent_bootstrap.markets.loader import load_marketplaces
from agent_bootstrap.renderers.json import render_json
from agent_bootstrap.renderers.markdown import render_apply_markdown, render_audit_markdown, render_plan_markdown


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    cwd = Path.cwd()
    runner = CommandRunner()
    if args.command == "apply":
        result = apply_change_set(args.change_set, runner, args.confirm)
        _emit_output(render_json(result) if args.format == "json" else render_apply_markdown(result))
        return 0
    profile_path = Path(args.profile)
    profile = load_profile(profile_path)
    audit = collect_audit(profile, args.agent, cwd, Path.home(), runner)

    if args.command == "audit":
        _emit_output(render_json(audit) if args.format == "json" else render_audit_markdown(audit))
        return 0
    if args.command == "plan":
        marketplaces = _load_profile_marketplaces(profile, profile_path.parent)
        plan = build_install_plan(audit, marketplaces)
        _emit_output(render_json(plan) if args.format == "json" else render_plan_markdown(plan))
        return 0
    if args.command == "verify":
        _emit_output(render_json(audit) if args.format == "json" else render_audit_markdown(audit))
        return 0
    parser.error(f"unsupported command: {args.command}")
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-bootstrap")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("audit", "plan", "verify"):
        sub = subparsers.add_parser(command)
        sub.add_argument("--profile", default="config/profiles/default.yaml")
        sub.add_argument("--agent", choices=["auto", "codex", "claude-code", "generic"], default="auto")
        sub.add_argument("--format", choices=["markdown", "json"], default="markdown")
    apply = subparsers.add_parser("apply")
    apply.add_argument("--profile", default="config/profiles/default.yaml")
    apply.add_argument("--change-set", required=True)
    apply.add_argument("--confirm", default="")
    apply.add_argument("--format", choices=["markdown", "json"], default="markdown")
    return parser


def collect_audit(
    profile: dict[str, Any],
    requested_agent: str,
    cwd: Path,
    home: Path,
    runner: CommandRunner,
) -> AuditResult:
    system, shell, arch = detect_os_shell_arch()
    tools = detect_core_tools(runner)
    package_managers = detect_package_managers(system, runner)
    capabilities = detect_workstation_capabilities(
        system,
        runner,
        home,
        str(profile.get("target_wsl_distro") or "Ubuntu-24.04"),
    )
    network = detect_network()
    agent_name = select_agent_name(profile.get("agent", requested_agent) if requested_agent == "auto" else requested_agent, runner)
    adapter_context = AdapterContext(cwd=cwd, home=home, runner=runner)
    adapter = _make_adapter(agent_name, adapter_context)
    adapter_audit = adapter.audit()

    missing: list[CapabilityFinding] = [finding for finding in tools.values() if not finding.present]
    for findings in capabilities.values():
        missing.extend(finding for finding in findings if not finding.present and finding.risk in {"high", "medium"})
    if not any(finding.present for finding in package_managers.values()):
        missing.append(
            CapabilityFinding(
                "package-manager",
                "Package manager",
                False,
                "medium",
                [item.evidence[0] for item in package_managers.values() if item.evidence],
                "Choose one OS-appropriate package manager only after user confirmation.",
            )
        )
    missing.extend(adapter_audit.missing)

    recommended: list[CapabilityFinding] = []
    recommended.extend(finding for finding in tools.values() if not finding.present)
    for findings in capabilities.values():
        recommended.extend(finding for finding in findings if not finding.present and finding.risk in {"low", "info"})
    recommended.extend(adapter_audit.recommended)

    risks = list(adapter_audit.risks)
    if not path_entries():
        risks.append("PATH is empty; command discovery may be unreliable.")
    for evidence in network:
        if evidence.status != "ok":
            risks.append("GitHub connectivity is not confirmed; check proxy, DNS, or firewall settings.")

    verification_commands = []
    for finding in tools.values():
        verification_commands.extend(e.verify_command for e in finding.evidence)
    for finding in package_managers.values():
        verification_commands.extend(e.verify_command for e in finding.evidence)
    for findings in capabilities.values():
        for finding in findings:
            verification_commands.extend(e.verify_command for e in finding.evidence)
    verification_commands.extend(adapter_audit.verification_commands)

    return AuditResult(
        os=system,
        shell=shell,
        arch=arch,
        tools=tools,
        package_managers=package_managers,
        network=network,
        agent=adapter_audit.agent,
        config_paths=adapter_audit.config_paths,
        installed_summary=adapter_audit.installed_summary,
        missing=missing,
        recommended=recommended,
        risks=_dedupe(risks),
        confirmation_required=_dedupe(adapter_audit.confirmation_required),
        verification_commands=_dedupe(verification_commands),
        capabilities=capabilities,
    )


def _make_adapter(agent_name: str, context: AdapterContext):
    if agent_name == "codex":
        return CodexAdapter(context)
    if agent_name == "claude-code":
        return ClaudeCodeAdapter(context)
    return GenericAdapter(context)


def _load_profile_marketplaces(profile: dict[str, Any], profile_dir: Path) -> list[dict[str, Any]]:
    paths = profile.get("marketplaces") or []
    return load_marketplaces(paths, base_dir=profile_dir.parent.parent if profile_dir.name == "profiles" else Path.cwd())


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _emit_output(text: str) -> None:
    try:
        print(text)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        sys.stdout.buffer.write(text.encode(encoding, errors="replace") + b"\n")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
