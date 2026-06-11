from __future__ import annotations

from agent_bootstrap.core.evidence import CommandRunner, tcp_evidence
from agent_bootstrap.core.model import CapabilityFinding, Evidence

from .git import detect_git
from .node import detect_node
from .python import detect_python


def detect_core_tools(runner: CommandRunner) -> dict[str, CapabilityFinding]:
    return {
        "git": detect_git(runner),
        "node": detect_node(runner),
        "python": detect_python(runner),
    }


def detect_network() -> list[Evidence]:
    return [tcp_evidence("github.com", 443)]
