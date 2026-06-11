from __future__ import annotations

from pathlib import Path

from agent_bootstrap.core.policy import marketplace_decision
from agent_bootstrap.markets.loader import load_marketplace
from agent_bootstrap.markets.validator import validate_marketplace_shape


ROOT = Path(__file__).resolve().parents[1]


def test_custom_marketplace_unpinned_third_party_is_audit_only():
    marketplace = load_marketplace(ROOT / "config" / "markets" / "custom.example.yaml")
    assert validate_marketplace_shape(marketplace) == []
    decision = marketplace_decision(marketplace)
    assert decision["can_plan"] is False
    assert any("unpinned" in item for item in decision["risks"])
    assert any("third-party" in item for item in decision["blocked"])


def test_official_marketplace_can_enter_plan_install():
    marketplace = load_marketplace(ROOT / "config" / "markets" / "codex-official.yaml")
    decision = marketplace_decision(marketplace)
    assert decision["can_recommend"] is True
    assert decision["can_plan"] is True
    assert decision["risks"] == []
