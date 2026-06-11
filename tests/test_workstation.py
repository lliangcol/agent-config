from __future__ import annotations

from pathlib import Path

from agent_bootstrap.detectors.workstation import detect_workstation_capabilities


def test_workstation_detector_builds_windows_wsl_capability_groups(tmp_path, fake_runner_factory):
    runner = fake_runner_factory(
        {
            "pwsh",
            "winget",
            "git",
            "ssh",
            "where.exe",
            "wsl",
            "volta",
            "node",
            "npm",
            "pnpm",
            "uv",
            "docker",
            "code",
        },
        {
            ("wsl", "-l", "-v"): "NAME STATE VERSION Ubuntu-24.04 Running 2",
            ("node", "-v"): "v22.19.0",
            ("python", "--version"): "Python 3.12.13",
            ("wsl", "-d", "Ubuntu-24.04", "--", "bash", "-lc", "node -v"): "v22.19.0",
            ("wsl", "-d", "Ubuntu-24.04", "--", "bash", "-lc", "python --version"): "Python 3.12.13",
            ("git", "config", "--global", "--get", "init.defaultBranch"): "main",
            ("git", "config", "--global", "--get", "core.autocrlf"): "false",
            ("git", "config", "--global", "--get", "core.eol"): "lf",
            ("git", "config", "--global", "--get", "pull.rebase"): "false",
            ("git", "config", "--global", "--get", "fetch.prune"): "true",
            ("git", "config", "--global", "--get", "credential.helper"): "manager",
        },
    )

    groups = detect_workstation_capabilities("Windows", runner, tmp_path)

    assert {"windows_base", "git_ssh", "wsl", "node_toolchain", "python_toolchain", "docker"} <= set(groups)
    assert any(item.name == "Ubuntu-24.04 distribution" and item.present for item in groups["wsl"])
    assert any(item.name == "Windows Node.js 22" and item.present for item in groups["node_toolchain"])


def test_workstation_detector_reports_node_major_mismatch(tmp_path, fake_runner_factory):
    runner = fake_runner_factory({"node"}, {("node", "-v"): "v24.0.0"})

    groups = detect_workstation_capabilities("Linux", runner, tmp_path)

    windows_node = next(item for item in groups["node_toolchain"] if item.name == "Windows Node.js 22")
    assert windows_node.present is False
    assert "Expected" in windows_node.recommendation
