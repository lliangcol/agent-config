from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from agent_bootstrap.core.evidence import CommandRunner
from agent_bootstrap.core.model import CapabilityFinding, Evidence


@dataclass
class AdapterContext:
    cwd: Path
    home: Path
    runner: CommandRunner
    env: dict[str, str] = field(default_factory=lambda: dict(os.environ))


@dataclass
class AdapterAudit:
    agent: str
    config_paths: list[Evidence]
    installed_summary: dict[str, object]
    missing: list[CapabilityFinding]
    recommended: list[CapabilityFinding]
    risks: list[str]
    confirmation_required: list[str]
    verification_commands: list[str]


class AgentAdapter(Protocol):
    name: str

    def audit(self) -> AdapterAudit:
        ...


def select_agent_name(requested: str, runner: CommandRunner, env: dict[str, str] | None = None) -> str:
    if requested in {"codex", "claude-code", "generic"}:
        return requested
    env = os.environ if env is None else env
    codex_available = runner.which("codex") is not None
    claude_available = runner.which("claude") is not None
    codex_env = any(key.startswith("CODEX") for key in env)
    claude_env = any(key.startswith("CLAUDE") for key in env)

    if codex_env and codex_available:
        return "codex"
    if claude_env and claude_available:
        return "claude-code"
    if codex_available and not claude_available:
        return "codex"
    if claude_available and not codex_available:
        return "claude-code"
    return "generic"


def make_missing_finding(kind: str, name: str, evidence: list[Evidence], recommendation: str) -> CapabilityFinding:
    return CapabilityFinding(
        kind=kind,
        name=name,
        present=False,
        risk="medium",
        evidence=evidence,
        recommendation=recommendation,
    )
