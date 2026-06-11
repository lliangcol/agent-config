from __future__ import annotations

from collections.abc import Sequence

from agent_bootstrap.core.model import Evidence
from agent_bootstrap.detectors.package_managers import detect_package_managers
from agent_bootstrap.detectors.runtimes import detect_core_tools


def test_windows_fixture_detects_winget(fake_runner_factory):
    runner = fake_runner_factory({"winget"})
    managers = detect_package_managers("Windows", runner)
    assert managers["winget"].present is True
    assert managers["scoop"].present is False


def test_macos_fixture_detects_brew(fake_runner_factory):
    runner = fake_runner_factory({"brew"})
    managers = detect_package_managers("Darwin", runner)
    assert managers["brew"].present is True


def test_linux_fixture_detects_apt(fake_runner_factory):
    runner = fake_runner_factory({"apt"})
    managers = detect_package_managers("Linux", runner)
    assert managers["apt"].present is True


def test_no_git_node_python_are_reported_missing(fake_runner_factory):
    runner = fake_runner_factory(set())
    tools = detect_core_tools(runner)
    assert tools["git"].present is False
    assert tools["node"].present is False
    assert tools["python"].present is False
    assert tools["git"].risk == "high"


def test_package_manager_presence_requires_successful_version_command():
    runner = ErrorRunner({"scoop"})
    managers = detect_package_managers("Windows", runner)
    assert managers["scoop"].present is False
    assert managers["scoop"].risk == "medium"
    assert "repair" in managers["scoop"].recommendation


class ErrorRunner:
    def __init__(self, available: set[str]):
        self.available = available

    def which(self, command: str) -> str | None:
        return f"/fake/bin/{command}" if command in self.available else None

    def run(self, args: Sequence[str], timeout: int = 10) -> Evidence:
        command = " ".join(args)
        if args and args[0] in self.available:
            return Evidence(command, "", "error", "command exited with 1", command)
        return Evidence(command, "", "missing", f"{args[0]} not found in PATH", command)
