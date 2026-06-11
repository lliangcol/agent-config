from __future__ import annotations

from agent_bootstrap.adapters.base import AdapterContext, select_agent_name
from agent_bootstrap.adapters.claude_code import ClaudeCodeAdapter
from agent_bootstrap.adapters.codex import CodexAdapter


def test_codex_only_adapter_reads_config_and_skills(tmp_path, fake_runner_factory):
    home = tmp_path / "home"
    cwd = tmp_path / "repo"
    (home / ".codex").mkdir(parents=True)
    (home / ".agents" / "skills" / "demo").mkdir(parents=True)
    cwd.mkdir()
    (home / ".codex" / "config.toml").write_text('[mcp_servers.docs]\ncommand = "docs"\n', encoding="utf-8")
    runner = fake_runner_factory({"codex"})
    audit = CodexAdapter(AdapterContext(cwd=cwd, home=home, runner=runner)).audit()
    assert audit.agent == "codex"
    assert audit.installed_summary["mcp_servers_configured"] == 1
    assert not any(item.name == "Codex CLI" for item in audit.missing)


def test_claude_only_adapter_detects_official_marketplace(tmp_path, fake_runner_factory):
    home = tmp_path / "home"
    cwd = tmp_path / "repo"
    (home / ".claude" / "plugins").mkdir(parents=True)
    cwd.mkdir()
    (home / ".claude" / "plugins" / "known_marketplaces.json").write_text(
        '{"claude-plugins-official":{"source":"anthropics/claude-plugins-official"}}',
        encoding="utf-8",
    )
    (cwd / ".mcp.json").write_text('{"mcpServers":{}}', encoding="utf-8")
    runner = fake_runner_factory({"claude"})
    audit = ClaudeCodeAdapter(AdapterContext(cwd=cwd, home=home, runner=runner)).audit()
    assert audit.agent == "claude-code"
    assert audit.installed_summary["official_marketplace_detected"] is True
    assert audit.installed_summary["mcp_config_detected"] is True


def test_auto_select_codex_or_claude_or_generic(fake_runner_factory):
    assert select_agent_name("auto", fake_runner_factory({"codex"})) == "codex"
    assert select_agent_name("auto", fake_runner_factory({"claude"})) == "claude-code"
    assert select_agent_name("auto", fake_runner_factory({"codex", "claude"}), env={}) == "generic"
    assert select_agent_name("auto", fake_runner_factory({"codex", "claude"}), env={"CODEX_HOME": "/tmp/codex"}) == "codex"
