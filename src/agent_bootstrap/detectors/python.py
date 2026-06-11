from __future__ import annotations

from agent_bootstrap.core.evidence import CommandRunner
from agent_bootstrap.core.model import CapabilityFinding


def detect_python(runner: CommandRunner) -> CapabilityFinding:
    evidence_items = []
    for command in ("python", "python3", "py"):
        evidence = runner.run([command, "--version"], timeout=5)
        evidence_items.append(evidence)
        if evidence.status == "ok":
            return CapabilityFinding(
                kind="runtime",
                name="Python",
                present=True,
                risk="low",
                evidence=evidence_items,
                recommendation="",
            )
    return CapabilityFinding(
        kind="runtime",
        name="Python",
        present=False,
        risk="high",
        evidence=evidence_items,
        recommendation="Install Python 3.11+ only after user confirmation; verify with python --version.",
    )
