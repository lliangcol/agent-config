from __future__ import annotations

from agent_bootstrap.core.evidence import CommandRunner
from agent_bootstrap.core.model import CapabilityFinding


def detect_git(runner: CommandRunner) -> CapabilityFinding:
    evidence = runner.run(["git", "--version"], timeout=5)
    present = evidence.status == "ok"
    return CapabilityFinding(
        kind="runtime",
        name="Git",
        present=present,
        risk="low" if present else "high",
        evidence=[evidence],
        recommendation="" if present else "Install Git and confirm it is available on PATH.",
    )
