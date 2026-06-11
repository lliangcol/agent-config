from __future__ import annotations

from pathlib import Path

from agent_bootstrap.core.model import AuditResult, CapabilityFinding, Evidence
from agent_bootstrap.core.planner import build_install_plan
from agent_bootstrap.markets.loader import load_marketplace
from agent_bootstrap.renderers.json import render_json
from agent_bootstrap.renderers.markdown import render_audit_markdown, render_plan_markdown


ROOT = Path(__file__).resolve().parents[1]


def test_official_plan_and_third_party_blocked_are_stable():
    audit = _audit("codex")
    markets = [
        load_marketplace(ROOT / "config" / "markets" / "codex-official.yaml"),
        load_marketplace(ROOT / "config" / "markets" / "custom.example.yaml"),
    ]
    plan = build_install_plan(audit, markets)
    assert any(action["marketplace"] == "openai-curated" for action in plan.actions)
    assert any(action["marketplace"] == "custom-example" for action in plan.blocked_actions)
    markdown = render_plan_markdown(plan)
    assert "# Agent Capability Install Plan" in markdown
    assert "Blocked Actions" in markdown


def test_markdown_and_json_renderers_are_stable():
    audit = _audit("generic")
    markdown = render_audit_markdown(audit)
    data = render_json(audit)
    assert "# Agent Capability Bootstrap Audit" in markdown
    assert '"agent": "generic"' in data


def test_json_renderer_escapes_non_ascii_for_windows_consoles():
    data = render_json({"marker": "✓"})
    assert "\\u2713" in data


def _audit(agent: str) -> AuditResult:
    evidence = Evidence("git --version", "git version fixture", "ok", "command exited with 0", "git --version")
    finding = CapabilityFinding("runtime", "Git", True, "low", [evidence], "")
    return AuditResult(
        os="Windows",
        shell="PowerShell",
        arch="AMD64",
        tools={"git": finding},
        package_managers={},
        network=[],
        agent=agent,
        config_paths=[],
        installed_summary={},
        missing=[],
        recommended=[],
        risks=[],
        confirmation_required=[],
        verification_commands=["git --version"],
    )
