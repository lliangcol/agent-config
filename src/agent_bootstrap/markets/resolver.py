from __future__ import annotations

from typing import Any

from agent_bootstrap.core.policy import marketplace_decision


def resolve_marketplace(marketplace: dict[str, Any]) -> dict[str, Any]:
    return marketplace_decision(marketplace)
