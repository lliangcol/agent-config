from __future__ import annotations

from agent_bootstrap.adapters.base import AdapterAudit, AdapterContext


class GenericAdapter:
    name = "generic"

    def __init__(self, context: AdapterContext):
        self.context = context

    def audit(self) -> AdapterAudit:
        return AdapterAudit(
            agent=self.name,
            config_paths=[],
            installed_summary={"note": "No Codex or Claude Code adapter selected; base environment only."},
            missing=[],
            recommended=[],
            risks=["Agent type is generic or ambiguous; agent-specific plugin, skill, and MCP rules were not mixed."],
            confirmation_required=["Choose Codex or Claude Code explicitly before generating agent-specific install actions."],
            verification_commands=[],
        )
