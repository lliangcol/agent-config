from __future__ import annotations

import os
from pathlib import Path

from agent_bootstrap.core.evidence import CommandRunner, missing_evidence, path_evidence, present_evidence
from agent_bootstrap.core.model import CapabilityFinding, Evidence


TARGET_WSL_DISTRO = "Ubuntu-24.04"


def detect_workstation_capabilities(
    system: str,
    runner: CommandRunner,
    home: Path,
    target_wsl_distro: str = TARGET_WSL_DISTRO,
) -> dict[str, list[CapabilityFinding]]:
    groups: dict[str, list[CapabilityFinding]] = {
        "windows_base": _detect_windows_base(system, runner),
        "git_ssh": _detect_git_ssh(system, runner),
        "wsl": _detect_wsl(system, runner, target_wsl_distro),
        "node_toolchain": _detect_node_toolchain(system, runner, target_wsl_distro),
        "python_toolchain": _detect_python_toolchain(system, runner, target_wsl_distro),
        "java_toolchain": _detect_java_toolchain(system, runner, target_wsl_distro),
        "docker": _detect_docker(system, runner, target_wsl_distro),
        "ide": _detect_ide(system, runner),
        "network_proxy": _detect_network_proxy(runner),
        "backup": _detect_backup_paths(home),
    }
    return {name: findings for name, findings in groups.items() if findings}


def _detect_windows_base(system: str, runner: CommandRunner) -> list[CapabilityFinding]:
    if system != "Windows":
        return []
    return [
        _command_finding("windows-base", "PowerShell 7", ["pwsh", "--version"], runner, "medium"),
        _command_finding("windows-base", "WinGet", ["winget", "--version"], runner, "high"),
        _command_finding(
            "windows-base",
            "PowerShell execution policy",
            ["pwsh", "-NoProfile", "-Command", "Get-ExecutionPolicy -List"],
            runner,
            "medium",
        ),
        _path_count_finding("windows-base", "PATH entries", os.environ.get("PATH", ""), os.pathsep),
    ]


def _detect_git_ssh(system: str, runner: CommandRunner) -> list[CapabilityFinding]:
    findings = [
        _command_finding("git-ssh", "Git version", ["git", "--version"], runner, "high"),
        _command_finding("git-ssh", "OpenSSH version", ["ssh", "-V"], runner, "high"),
        _github_ssh_finding(runner),
        _git_config_finding("Git user.name", "user.name", runner, "medium"),
        _git_config_finding("Git user.email", "user.email", runner, "medium"),
        _git_config_expected("Git init.defaultBranch", "init.defaultBranch", "main", runner, "medium"),
        _git_config_expected("Git core.autocrlf", "core.autocrlf", "false", runner, "medium"),
        _git_config_expected("Git core.eol", "core.eol", "lf", runner, "medium"),
        _git_config_expected("Git pull.rebase", "pull.rebase", "false", runner, "low"),
        _git_config_expected("Git fetch.prune", "fetch.prune", "true", runner, "low"),
        _git_config_expected("Git credential.helper", "credential.helper", "manager", runner, "low"),
        _git_config_finding("Git core.editor", "core.editor", runner, "low"),
    ]
    if system == "Windows":
        findings.insert(0, _command_finding("git-ssh", "Git path", ["where.exe", "git"], runner, "medium"))
        findings.insert(2, _command_finding("git-ssh", "OpenSSH path", ["where.exe", "ssh"], runner, "medium"))
    return findings


def _detect_wsl(system: str, runner: CommandRunner, distro: str) -> list[CapabilityFinding]:
    if system != "Windows":
        return []
    list_evidence = runner.run(["wsl", "-l", "-v"], timeout=10)
    distro_present = list_evidence.status == "ok" and distro.lower() in list_evidence.value.lower()
    return [
        CapabilityFinding(
            "wsl",
            "WSL distribution list",
            list_evidence.status == "ok",
            "medium" if list_evidence.status != "ok" else "low",
            [list_evidence],
            "" if list_evidence.status == "ok" else "Enable WSL only after confirmation; verify with wsl -l -v.",
        ),
        CapabilityFinding(
            "wsl",
            f"{distro} distribution",
            distro_present,
            "high" if not distro_present else "low",
            [list_evidence],
            "" if distro_present else f"Install {distro} only after confirmation; verify with wsl -l -v.",
        ),
        _wsl_command_finding(distro, "WSL uname", "uname -a", runner, "medium"),
    ]


def _detect_node_toolchain(system: str, runner: CommandRunner, distro: str) -> list[CapabilityFinding]:
    findings = [
        _command_finding("node-toolchain", "Windows Volta", ["volta", "--version"], runner, "high"),
        _version_prefix_finding("node-toolchain", "Windows Node.js 22", ["node", "-v"], runner, "v22.", "medium"),
        _command_finding("node-toolchain", "Windows npm", ["npm", "-v"], runner, "medium"),
        _command_finding("node-toolchain", "Windows pnpm", ["pnpm", "-v"], runner, "medium"),
    ]
    if system == "Windows":
        findings.extend(
            [
                _wsl_command_finding(distro, "WSL fnm", "fnm --version", runner, "medium"),
                _wsl_version_prefix_finding(distro, "WSL Node.js 22", "node -v", "v22.", runner, "medium"),
                _wsl_command_finding(distro, "WSL npm", "npm -v", runner, "medium"),
                _wsl_command_finding(distro, "WSL pnpm", "pnpm -v", runner, "medium"),
            ]
        )
    return findings


def _detect_python_toolchain(system: str, runner: CommandRunner, distro: str) -> list[CapabilityFinding]:
    findings = [
        _command_finding("python-toolchain", "Windows uv", ["uv", "--version"], runner, "high"),
        _version_prefix_finding(
            "python-toolchain", "Windows Python 3.12", ["python", "--version"], runner, "Python 3.12", "medium"
        ),
        _command_finding("python-toolchain", "Windows uv python list", ["uv", "python", "list"], runner, "low", timeout=15),
    ]
    if system == "Windows":
        findings.extend(
            [
                _wsl_command_finding(distro, "WSL uv", "uv --version", runner, "medium"),
                _wsl_version_prefix_finding(distro, "WSL Python 3.12", "python --version", "Python 3.12", runner, "medium"),
            ]
        )
    return findings


def _detect_java_toolchain(system: str, runner: CommandRunner, distro: str) -> list[CapabilityFinding]:
    if system != "Windows":
        return []
    return [
        _wsl_command_finding(distro, "WSL Java", "java -version", runner, "medium"),
        _wsl_command_finding(distro, "WSL javac", "javac -version", runner, "medium"),
        _wsl_command_finding(distro, "WSL Maven", "mvn -version", runner, "medium"),
    ]


def _detect_docker(system: str, runner: CommandRunner, distro: str) -> list[CapabilityFinding]:
    findings = [
        _command_finding("docker", "Windows Docker CLI", ["docker", "--version"], runner, "medium"),
        _command_finding("docker", "Windows Docker Compose", ["docker", "compose", "version"], runner, "medium"),
    ]
    if system == "Windows":
        findings.extend(
            [
                _wsl_command_finding(distro, "WSL Docker CLI", "docker version", runner, "medium", timeout=15),
                _wsl_command_finding(distro, "WSL Docker Compose", "docker compose version", runner, "medium"),
            ]
        )
    return findings


def _detect_ide(system: str, runner: CommandRunner) -> list[CapabilityFinding]:
    findings = [
        _command_finding("ide", "VS Code CLI", ["code", "--version"], runner, "low"),
        _command_finding("ide", "Zed CLI", ["zed", "--version"], runner, "info"),
    ]
    if system == "Windows":
        findings.append(_command_finding("ide", "IntelliJ IDEA winget search", ["winget", "list", "--name", "IntelliJ"], runner, "info"))
    return findings


def _detect_network_proxy(runner: CommandRunner) -> list[CapabilityFinding]:
    proxy_vars = {key: os.environ.get(key, "") for key in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy")}
    detected = ", ".join(f"{key}={value}" for key, value in proxy_vars.items() if value) or "none"
    return [
        CapabilityFinding(
            "network-proxy",
            "Proxy environment variables",
            True,
            "low",
            [present_evidence("inspect proxy environment", detected, "Get-ChildItem Env:*PROXY*")],
            "Proxy variables are advisory evidence; configure only after confirmation if GitHub or package registries are unreachable.",
        ),
        _command_finding("network-proxy", "Git HTTP proxy", ["git", "config", "--global", "--get", "http.proxy"], runner, "info"),
        _command_finding("network-proxy", "Git HTTPS proxy", ["git", "config", "--global", "--get", "https.proxy"], runner, "info"),
        _command_finding("network-proxy", "npm proxy", ["npm", "config", "get", "proxy"], runner, "info"),
        _command_finding("network-proxy", "npm HTTPS proxy", ["npm", "config", "get", "https-proxy"], runner, "info"),
    ]


def _detect_backup_paths(home: Path) -> list[CapabilityFinding]:
    paths = [
        (home / ".ssh", "Windows SSH directory"),
        (home / ".gitconfig", "Windows Git config"),
        (home / ".wslconfig", "Windows WSL config"),
        (home / ".npmrc", "Windows npm config"),
        (home / ".codex", "Codex user state"),
        (home / ".claude", "Claude user state"),
    ]
    return [
        CapabilityFinding(
            "backup",
            label,
            evidence.status == "ok",
            "low" if evidence.status == "ok" else "info",
            [evidence],
            "" if evidence.status == "ok" else "Advisory only: include this path in private backup when it exists.",
        )
        for path, label in paths
        for evidence in [path_evidence(path, label)]
    ]


def _command_finding(
    kind: str,
    name: str,
    args: list[str],
    runner: CommandRunner,
    missing_risk: str,
    timeout: int = 5,
) -> CapabilityFinding:
    evidence = runner.run(args, timeout=timeout)
    present = evidence.status == "ok"
    return CapabilityFinding(
        kind=kind,
        name=name,
        present=present,
        risk="low" if present else missing_risk,
        evidence=[evidence],
        recommendation="" if present else f"Review or configure {name} only after confirmation; verify with {evidence.verify_command}.",
    )


def _version_prefix_finding(
    kind: str,
    name: str,
    args: list[str],
    runner: CommandRunner,
    expected_prefix: str,
    mismatch_risk: str,
) -> CapabilityFinding:
    evidence = runner.run(args, timeout=5)
    present = evidence.status == "ok" and evidence.value.strip().startswith(expected_prefix)
    return CapabilityFinding(
        kind=kind,
        name=name,
        present=present,
        risk="low" if present else mismatch_risk,
        evidence=[evidence],
        recommendation="" if present else f"Expected {name} to report {expected_prefix}; change only after confirmation.",
    )


def _wsl_command_finding(
    distro: str,
    name: str,
    command: str,
    runner: CommandRunner,
    missing_risk: str,
    timeout: int = 10,
) -> CapabilityFinding:
    args = ["wsl", "-d", distro, "--", "bash", "-lc", command]
    evidence = runner.run(args, timeout=timeout)
    present = evidence.status == "ok"
    return CapabilityFinding(
        kind="wsl",
        name=name,
        present=present,
        risk="low" if present else missing_risk,
        evidence=[evidence],
        recommendation="" if present else f"Review WSL {distro} setup only after confirmation; verify with {evidence.verify_command}.",
    )


def _wsl_version_prefix_finding(
    distro: str,
    name: str,
    command: str,
    expected_prefix: str,
    runner: CommandRunner,
    mismatch_risk: str,
) -> CapabilityFinding:
    args = ["wsl", "-d", distro, "--", "bash", "-lc", command]
    evidence = runner.run(args, timeout=10)
    present = evidence.status == "ok" and evidence.value.strip().startswith(expected_prefix)
    return CapabilityFinding(
        kind="wsl",
        name=name,
        present=present,
        risk="low" if present else mismatch_risk,
        evidence=[evidence],
        recommendation="" if present else f"Expected {name} to report {expected_prefix}; change only after confirmation.",
    )


def _github_ssh_finding(runner: CommandRunner) -> CapabilityFinding:
    evidence = runner.run(["ssh", "-o", "BatchMode=yes", "-T", "git@github.com"], timeout=10)
    output = evidence.value.lower()
    present = evidence.status == "ok" or "successfully authenticated" in output
    return CapabilityFinding(
        "git-ssh",
        "GitHub SSH authentication",
        present,
        "medium" if not present else "low",
        [evidence],
        "" if present else "Configure GitHub SSH only after user confirmation; verify with ssh -T git@github.com.",
    )


def _git_config_finding(name: str, key: str, runner: CommandRunner, missing_risk: str) -> CapabilityFinding:
    evidence = runner.run(["git", "config", "--global", "--get", key], timeout=5)
    present = evidence.status == "ok" and bool(evidence.value.strip())
    return CapabilityFinding(
        "git-ssh",
        name,
        present,
        "low" if present else missing_risk,
        [evidence],
        "" if present else f"Set {key} only after confirmation; verify with git config --global --get {key}.",
    )


def _git_config_expected(name: str, key: str, expected: str, runner: CommandRunner, mismatch_risk: str) -> CapabilityFinding:
    evidence = runner.run(["git", "config", "--global", "--get", key], timeout=5)
    present = evidence.status == "ok" and evidence.value.strip() == expected
    return CapabilityFinding(
        "git-ssh",
        name,
        present,
        "low" if present else mismatch_risk,
        [evidence],
        "" if present else f"Expected {key}={expected}; change only after confirmation.",
    )


def _path_count_finding(kind: str, name: str, value: str, separator: str) -> CapabilityFinding:
    entries = [entry for entry in value.split(separator) if entry]
    evidence = present_evidence("inspect PATH", str(len(entries)), "echo $env:PATH")
    return CapabilityFinding(kind, name, bool(entries), "low" if entries else "medium", [evidence], "")
