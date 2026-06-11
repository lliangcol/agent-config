from __future__ import annotations

from pathlib import Path

from agent_bootstrap.adapters.base import AdapterAudit, AdapterContext
from agent_bootstrap.core.evidence import path_evidence
from agent_bootstrap.core.model import CapabilityFinding
from agent_bootstrap.adapters.codex import evidence_summary


class ClaudeCodeAdapter:
    name = "claude-code"

    def __init__(self, context: AdapterContext):
        self.context = context

    def audit(self) -> AdapterAudit:
        runner = self.context.runner
        version = runner.run(["claude", "--version"], timeout=5)
        command_evidence = [version]
        if version.status == "ok":
            command_evidence.extend(
                [
                    runner.run(["claude", "plugin", "list", "--json"], timeout=10),
                    runner.run(["claude", "plugin", "marketplace", "list", "--json"], timeout=10),
                    runner.run(["claude", "mcp", "list"], timeout=10),
                ]
            )

        config_paths = [
            path_evidence(self.context.home / ".claude" / "skills", "Claude user skills"),
            path_evidence(self.context.cwd / ".claude" / "skills", "Claude project skills"),
            path_evidence(self.context.cwd / ".claude" / "settings.json", "Claude project settings"),
            path_evidence(self.context.cwd / ".claude" / "settings.local.json", "Claude local settings"),
            path_evidence(self.context.cwd / ".mcp.json", "Claude project MCP config"),
            path_evidence(self.context.home / ".claude.json", "Claude user/local MCP and project state"),
            path_evidence(self.context.home / ".claude" / "plugins" / "known_marketplaces.json", "Claude known marketplaces"),
        ]
        marketplace_detected = _contains_any(config_paths, ["claude-plugins-official", "anthropics/claude-plugins-official"])
        mcp_detected = _contains_any(config_paths, ['"mcpServers"', '"mcp_servers"'])
        installed_summary = {
            "cli": evidence_summary(command_evidence),
            "config_paths": evidence_summary(config_paths),
            "official_marketplace_detected": marketplace_detected,
            "mcp_config_detected": mcp_detected,
        }

        missing: list[CapabilityFinding] = []
        recommended: list[CapabilityFinding] = []
        if version.status != "ok":
            missing.append(
                CapabilityFinding(
                    "agent-cli",
                    "Claude Code CLI",
                    False,
                    "high",
                    [version],
                    "Install or enable Claude Code only after confirmation; verify with claude --version.",
                )
            )
        if not marketplace_detected:
            recommended.append(
                CapabilityFinding(
                    "marketplace",
                    "Claude official marketplace",
                    False,
                    "low",
                    config_paths,
                    "Plan official marketplace availability as claude-plugins-official; validate against current Claude Code docs before install.",
                )
            )
        if not mcp_detected:
            recommended.append(
                CapabilityFinding(
                    "mcp",
                    "Claude Code MCP configuration",
                    False,
                    "medium",
                    config_paths,
                    "Plan .mcp.json or claude mcp configuration; do not run claude mcp add without confirmation.",
                )
            )

        return AdapterAudit(
            agent=self.name,
            config_paths=config_paths,
            installed_summary=installed_summary,
            missing=missing,
            recommended=recommended,
            risks=[],
            confirmation_required=[
                "Run claude plugin validate . only as validation, not as installation.",
                "Use /reload-plugins only as a post-install user prompt after confirmed plugin changes.",
            ],
            verification_commands=[
                "claude --version",
                "claude plugin list --json",
                "claude plugin marketplace list --json",
                "claude mcp list",
                "claude plugin validate .",
            ],
        )


def _contains_any(config_paths: list, needles: list[str]) -> bool:
    for evidence in config_paths:
        if evidence.status != "ok":
            continue
        path = Path(evidence.value).expanduser()
        if path.is_dir():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if any(needle in text for needle in needles):
            return True
    return False
