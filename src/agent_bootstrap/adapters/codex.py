from __future__ import annotations

from pathlib import Path

from agent_bootstrap.adapters.base import AdapterAudit, AdapterContext
from agent_bootstrap.core.evidence import path_evidence
from agent_bootstrap.core.model import CapabilityFinding, Evidence
from agent_bootstrap.detectors.repositories import find_git_root_by_filesystem


class CodexAdapter:
    name = "codex"

    def __init__(self, context: AdapterContext):
        self.context = context

    def audit(self) -> AdapterAudit:
        runner = self.context.runner
        version = runner.run(["codex", "--version"], timeout=5)
        command_evidence = [version]
        if version.status == "ok":
            command_evidence.extend(
                [
                    runner.run(["codex", "doctor", "--json"], timeout=20),
                    runner.run(["codex", "plugin", "marketplace", "list"], timeout=10),
                    runner.run(["codex", "plugin", "list"], timeout=10),
                    runner.run(["codex", "mcp", "--help"], timeout=10),
                ]
            )

        config_paths = [
            path_evidence(self.context.home / ".codex" / "config.toml", "Codex user config"),
            path_evidence(self.context.cwd / ".codex" / "config.toml", "Codex project config"),
        ]
        skill_paths = self._skill_paths()
        skill_evidence = [path_evidence(path, "Codex skill directory") for path in skill_paths]
        mcp_count = _count_codex_mcp_servers(config_paths)
        plugin_config_count = _count_codex_plugin_entries(config_paths)
        installed_summary = {
            "cli": evidence_summary(command_evidence),
            "config_paths": evidence_summary(config_paths),
            "skill_directories": evidence_summary(skill_evidence),
            "mcp_servers_configured": mcp_count,
            "plugins_configured": plugin_config_count,
        }

        missing: list[CapabilityFinding] = []
        recommended: list[CapabilityFinding] = []
        risks: list[str] = []
        confirmations = ["Install Codex plugins, skills, apps, or MCP servers only after explicit user confirmation."]

        if version.status != "ok":
            missing.append(
                CapabilityFinding(
                    "agent-cli",
                    "Codex CLI",
                    False,
                    "high",
                    [version],
                    "Install or enable Codex CLI only after confirmation; verify with codex --version.",
                )
            )
        if not any(item.status == "ok" for item in skill_evidence):
            recommended.append(
                CapabilityFinding(
                    "skill",
                    "Codex skill directory",
                    False,
                    "low",
                    skill_evidence,
                    "Use repo .agents/skills or user $HOME/.agents/skills when the user chooses to install this skill.",
                )
            )
        if mcp_count == 0:
            recommended.append(
                CapabilityFinding(
                    "mcp",
                    "Codex MCP configuration",
                    False,
                    "medium",
                    config_paths,
                    "Plan MCP server configuration in config.toml; do not run codex mcp add without confirmation.",
                )
            )

        verification = [
            "codex --version",
            "codex plugin marketplace list",
            "codex plugin list",
            "codex mcp --help",
        ]
        return AdapterAudit(
            agent=self.name,
            config_paths=config_paths,
            installed_summary=installed_summary,
            missing=missing,
            recommended=recommended,
            risks=risks,
            confirmation_required=confirmations,
            verification_commands=verification,
        )

    def _skill_paths(self) -> list[Path]:
        root = find_git_root_by_filesystem(self.context.cwd)
        repo_paths: list[Path] = []
        if root:
            current = self.context.cwd.resolve()
            while True:
                repo_paths.append(current / ".agents" / "skills")
                if current == root:
                    break
                current = current.parent
        else:
            repo_paths.append(self.context.cwd / ".agents" / "skills")
        paths = repo_paths + [self.context.home / ".agents" / "skills"]
        admin = Path("/etc/codex/skills")
        if admin.exists():
            paths.append(admin)
        return paths


def _count_codex_mcp_servers(config_paths: list[Evidence]) -> int:
    return _count_toml_tables(config_paths, "[mcp_servers.")


def _count_codex_plugin_entries(config_paths: list[Evidence]) -> int:
    return _count_toml_tables(config_paths, '[plugins."')


def _count_toml_tables(config_paths: list[Evidence], marker: str) -> int:
    count = 0
    for evidence in config_paths:
        if evidence.status != "ok":
            continue
        path = Path(evidence.value).expanduser()
        try:
            count += path.read_text(encoding="utf-8").count(marker)
        except OSError:
            continue
    return count


def evidence_summary(items: list[Evidence]) -> list[dict[str, str]]:
    return [
        {
            "command": item.command,
            "status": item.status,
            "value": item.value,
            "reason": item.reason,
            "verify_command": item.verify_command,
        }
        for item in items
    ]
