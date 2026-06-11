from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REMOTE_SOURCE_TYPES = {"github", "git", "url"}
TRUST_LEVELS = {"official", "organization", "personal", "third-party", "unknown"}
MODES = {"audit-only", "plan-install", "execute-after-confirm", "verify-only"}


def load_yaml_file(path: str | Path) -> Any:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
        return {} if loaded is None else loaded
    except Exception:
        return json.loads(text)


def load_profile(path: str | Path) -> dict[str, Any]:
    data = load_yaml_file(path)
    if not isinstance(data, dict):
        raise ValueError(f"profile must be an object: {path}")
    return data


def marketplace_decision(marketplace: dict[str, Any]) -> dict[str, Any]:
    source = marketplace.get("source") or {}
    trust = marketplace.get("trust") or {}
    policy = marketplace.get("policy") or {}
    source_type = source.get("type", "unknown")
    trust_level = trust.get("level", "unknown")
    pinned = bool(trust.get("pinned")) or bool(source.get("ref"))
    requested_mode = policy.get("default_mode", "audit-only")

    risks: list[str] = []
    blocked: list[str] = []
    confirmation: list[str] = []

    if trust_level not in TRUST_LEVELS:
        risks.append(f"unknown trust level: {trust_level}")
        trust_level = "unknown"
    if requested_mode not in MODES:
        risks.append(f"unknown mode: {requested_mode}")
        requested_mode = "audit-only"
    if source_type in REMOTE_SOURCE_TYPES and not pinned:
        risks.append(f"unpinned remote source: {source_type}")

    can_recommend = False
    can_plan = False
    if trust_level == "official":
        can_recommend = True
        can_plan = requested_mode in {"plan-install", "execute-after-confirm"}
    elif trust_level in {"organization", "personal"}:
        can_recommend = True
        can_plan = requested_mode == "plan-install" and not risks
        confirmation.append("organization/personal marketplace requires explicit user confirmation")
    else:
        can_recommend = False
        can_plan = False
        blocked.append("third-party or unknown marketplace remains audit-only by default")

    if requested_mode == "execute-after-confirm":
        blocked.append("execute-after-confirm is modeled but not executable in v1")
        confirmation.append("execution mode requires a separate explicit confirmation and executor")
        can_plan = False
    if source_type in REMOTE_SOURCE_TYPES and not pinned:
        blocked.append("unpinned remote marketplace is blocked from install planning")
        can_plan = False

    return {
        "name": marketplace.get("name", "unknown"),
        "source_type": source_type,
        "trust_level": trust_level,
        "requested_mode": requested_mode,
        "can_recommend": can_recommend,
        "can_plan": can_plan,
        "risks": risks,
        "blocked": blocked,
        "confirmation": confirmation,
    }
