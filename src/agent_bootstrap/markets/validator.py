from __future__ import annotations

from typing import Any


REQUIRED_TOP_LEVEL = {"agent", "name", "source", "trust", "policy", "capabilities", "validation_commands"}
SOURCE_TYPES = {"official", "github", "git", "url", "local"}
TRUST_LEVELS = {"official", "organization", "personal", "third-party", "unknown"}
MODES = {"audit-only", "plan-install", "execute-after-confirm"}


def validate_marketplace_shape(marketplace: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_TOP_LEVEL - set(marketplace)
    if missing:
        errors.append("missing fields: " + ", ".join(sorted(missing)))
    source = marketplace.get("source") or {}
    trust = marketplace.get("trust") or {}
    policy = marketplace.get("policy") or {}
    if source.get("type") not in SOURCE_TYPES:
        errors.append("source.type must be one of official, github, git, url, local")
    if trust.get("level") not in TRUST_LEVELS:
        errors.append("trust.level is invalid")
    if policy.get("default_mode") not in MODES:
        errors.append("policy.default_mode is invalid")
    if not isinstance(marketplace.get("validation_commands", []), list):
        errors.append("validation_commands must be a list")
    return errors
