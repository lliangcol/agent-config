from __future__ import annotations

from agent_bootstrap.core.evidence import CommandRunner
from agent_bootstrap.core.model import CapabilityFinding


def detect_node(runner: CommandRunner) -> CapabilityFinding:
    evidence = runner.run(["node", "--version"], timeout=5)
    present = evidence.status == "ok"
    return CapabilityFinding(
        kind="runtime",
        name="Node.js",
        present=present,
        risk="low" if present else "medium",
        evidence=[evidence],
        recommendation="" if present else "Install Node.js only after user confirmation; verify with node --version.",
    )
