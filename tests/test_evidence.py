from __future__ import annotations

import os
import sys
from types import SimpleNamespace
from pathlib import Path

from agent_bootstrap.core import evidence as evidence_module
from agent_bootstrap.core.evidence import CommandRunner, path_verify_command


def test_path_verify_command_matches_host_shell_family():
    command = path_verify_command(Path("C:/Users/example/config.toml"))
    if os.name == "nt":
        assert command.startswith("Test-Path -LiteralPath ")
    else:
        assert command.startswith("test -e ")


def test_command_runner_replaces_undecodable_output():
    evidence = CommandRunner().run(
        [sys.executable, "-c", "import sys; sys.stdout.buffer.write(bytes([0xff]))"],
        timeout=5,
    )
    assert evidence.status == "ok"
    assert evidence.value


def test_command_runner_executes_windows_powershell_shims(monkeypatch):
    calls = {}

    def fake_which(command):
        if command == "scoop":
            return r"D:\Scoop\shims\scoop.ps1"
        if command == "pwsh":
            return r"C:\Program Files\PowerShell\7\pwsh.exe"
        return None

    def fake_run(args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout="scoop ok", stderr="")

    monkeypatch.setattr(evidence_module, "_is_windows_host", lambda: True)
    monkeypatch.setattr(evidence_module.shutil, "which", fake_which)
    monkeypatch.setattr(evidence_module.subprocess, "run", fake_run)

    result = CommandRunner().run(["scoop", "--version"], timeout=5)

    assert result.status == "ok"
    assert result.command == "scoop --version"
    assert calls["args"] == [
        r"C:\Program Files\PowerShell\7\pwsh.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        r"D:\Scoop\shims\scoop.ps1",
        "--version",
    ]
    assert calls["kwargs"]["shell"] is False
