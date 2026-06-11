from __future__ import annotations

from agent_bootstrap.core.evidence import CommandRunner
from agent_bootstrap.core.model import CapabilityFinding


PACKAGE_MANAGERS = {
    "Windows": ["winget", "scoop", "choco"],
    "Darwin": ["brew", "port"],
    "Linux": ["apt", "dnf", "yum", "pacman", "apk", "zypper", "brew"],
}

WINDOWS_PACKAGE_MANAGER_POLICY = {
    "winget": {
        "missing_risk": "high",
        "recommendation": "Install or repair WinGet/App Installer only after user confirmation; it is the preferred Windows package manager.",
    },
    "scoop": {
        "missing_risk": "low",
        "recommendation": "Scoop is optional; use it only for helper CLI tools such as ripgrep, jq, or tree.",
    },
    "choco": {
        "missing_risk": "info",
        "recommendation": "Chocolatey is not part of the default workstation baseline; install only for a specific confirmed need.",
    },
}


def detect_package_managers(system: str, runner: CommandRunner) -> dict[str, CapabilityFinding]:
    result: dict[str, CapabilityFinding] = {}
    for command in PACKAGE_MANAGERS.get(system, ["brew", "apt", "winget"]):
        evidence = runner.run([command, "--version"], timeout=5)
        present = evidence.status == "ok"
        missing_risk = "medium"
        recommendation = f"Install, repair, or enable {command} only after user confirmation."
        if system == "Windows":
            policy = WINDOWS_PACKAGE_MANAGER_POLICY.get(command, {})
            missing_risk = policy.get("missing_risk", missing_risk)
            recommendation = policy.get("recommendation", recommendation)
        if evidence.status == "error":
            missing_risk = "medium"
            recommendation = f"repair or enable {command} only after user confirmation; command exists but did not run cleanly."
        result[command] = CapabilityFinding(
            kind="package-manager",
            name=command,
            present=present,
            risk="low" if present else missing_risk,
            recommendation="" if present else recommendation,
            evidence=[evidence],
        )
    return result
