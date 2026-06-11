from __future__ import annotations

from pathlib import Path

from agent_bootstrap import cli
from agent_bootstrap.cli import main
from agent_bootstrap.core.model import Evidence


def test_cli_audit_json_smoke(capsys, monkeypatch, fake_runner_factory):
    _patch_cli_environment(monkeypatch, fake_runner_factory)
    rc = main(["audit", "--profile", "config/profiles/default.yaml", "--agent", "generic", "--format", "json"])
    out = capsys.readouterr().out
    assert rc == 0
    assert '"agent": "generic"' in out
    assert '"capabilities"' in out


def test_cli_plan_markdown_smoke(capsys, monkeypatch, fake_runner_factory):
    _patch_cli_environment(monkeypatch, fake_runner_factory)
    rc = main(["plan", "--profile", "config/profiles/default.yaml", "--agent", "generic", "--format", "markdown"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "custom-example" in out


def test_cli_apply_dry_run_smoke(capsys):
    rc = main(
        [
            "apply",
            "--change-set",
            "config/change-sets/windows-dev-safe.example.yaml",
            "--format",
            "json",
        ]
    )
    out = capsys.readouterr().out
    assert rc == 0
    assert '"dry_run": true' in out
    assert '"skipped"' in out


def _patch_cli_environment(monkeypatch, fake_runner_factory):
    runner = fake_runner_factory({"git", "python", "winget"}, {("python", "--version"): "Python 3.12.13"})
    monkeypatch.setattr(cli, "CommandRunner", lambda: runner)
    monkeypatch.setattr(cli, "detect_network", lambda: [Evidence("tcp github.com:443", "github.com:443", "ok", "fixture", "tcp github.com:443")])
