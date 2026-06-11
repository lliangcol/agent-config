from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any


@dataclass(frozen=True)
class Evidence:
    command: str
    value: str
    status: str
    reason: str
    verify_command: str


@dataclass(frozen=True)
class CapabilityFinding:
    kind: str
    name: str
    present: bool
    risk: str
    evidence: list[Evidence] = field(default_factory=list)
    recommendation: str = ""


@dataclass(frozen=True)
class AuditResult:
    os: str
    shell: str
    arch: str
    tools: dict[str, CapabilityFinding]
    package_managers: dict[str, CapabilityFinding]
    network: list[Evidence]
    agent: str
    config_paths: list[Evidence]
    installed_summary: dict[str, Any]
    missing: list[CapabilityFinding]
    recommended: list[CapabilityFinding]
    risks: list[str]
    confirmation_required: list[str]
    verification_commands: list[str]
    capabilities: dict[str, list[CapabilityFinding]] = field(default_factory=dict)


@dataclass(frozen=True)
class ApplyActionResult:
    id: str
    kind: str
    title: str
    status: str
    command: str
    reason: str
    evidence: Evidence | None = None


@dataclass(frozen=True)
class ApplyResult:
    mode: str
    dry_run: bool
    change_set: str
    executed: list[ApplyActionResult]
    blocked: list[ApplyActionResult]
    skipped: list[ApplyActionResult]
    confirmation_required: list[str]
    risks: list[str]


@dataclass(frozen=True)
class InstallPlan:
    mode: str
    actions: list[dict[str, Any]]
    blocked_actions: list[dict[str, Any]]
    validation_steps: list[str]
    confirmation_required: list[str]
    risk_summary: list[str]


def to_dict(value: Any) -> Any:
    if is_dataclass(value):
        return {k: to_dict(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): to_dict(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_dict(item) for item in value]
    return value
