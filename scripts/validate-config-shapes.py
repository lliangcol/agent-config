#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

from agent_bootstrap.core.policy import load_profile
from agent_bootstrap.markets.loader import load_marketplace
from agent_bootstrap.markets.validator import validate_marketplace_shape

PROFILE_AGENTS = {"auto", "codex", "claude-code", "generic"}
ALLOWED_CHANGE_ACTION_TYPES = {"git_config", "powershell_execution_policy", "user_env"}


def main() -> int:
    errors: list[str] = []
    profile_paths = sorted((ROOT / "config" / "profiles").glob("*.yaml"))
    marketplace_paths = sorted((ROOT / "config" / "markets").glob("*.yaml"))
    change_set_paths = sorted((ROOT / "config" / "change-sets").glob("*.yaml"))

    for path in profile_paths:
        try:
            profile = load_profile(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: failed to load profile: {exc}")
            continue
        errors.extend(_profile_errors(path, profile))

    for path in marketplace_paths:
        try:
            marketplace = load_marketplace(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: failed to load marketplace: {exc}")
            continue
        errors.extend(f"{path.relative_to(ROOT)}: {error}" for error in validate_marketplace_shape(marketplace))

    for path in change_set_paths:
        try:
            change_set = load_marketplace(path)
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: failed to load change set: {exc}")
            continue
        errors.extend(_change_set_errors(path, change_set))

    if errors:
        for error in errors:
            print(error)
        return 1
    print(
        f"config shapes ok: profiles={len(profile_paths)}, "
        f"marketplaces={len(marketplace_paths)}, change_sets={len(change_set_paths)}"
    )
    return 0


def _profile_errors(path: Path, profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT)
    for field in ("name", "agent", "required_tools", "marketplaces"):
        if field not in profile:
            errors.append(f"{rel}: missing profile field: {field}")
    if profile.get("agent") not in PROFILE_AGENTS:
        errors.append(f"{rel}: agent is invalid")
    if not isinstance(profile.get("required_tools", []), list):
        errors.append(f"{rel}: required_tools must be a list")
    package_managers = profile.get("package_managers", [])
    if package_managers and not isinstance(package_managers, (list, dict)):
        errors.append(f"{rel}: package_managers must be a list or object")
    if isinstance(package_managers, dict):
        for key in ("required", "optional", "advisory"):
            if key in package_managers and not isinstance(package_managers[key], list):
                errors.append(f"{rel}: package_managers.{key} must be a list")
    marketplaces = profile.get("marketplaces", [])
    if not isinstance(marketplaces, list):
        errors.append(f"{rel}: marketplaces must be a list")
        return errors
    for item in marketplaces:
        if not isinstance(item, str):
            errors.append(f"{rel}: marketplace path must be a string")
            continue
        candidate = Path(item)
        if not candidate.is_absolute():
            candidate = ROOT / candidate
        if not candidate.exists():
            errors.append(f"{rel}: marketplace path does not exist: {item}")
    return errors


def _change_set_errors(path: Path, change_set: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT)
    if "name" not in change_set:
        errors.append(f"{rel}: missing change set field: name")
    actions = change_set.get("actions")
    if not isinstance(actions, list):
        return [*errors, f"{rel}: actions must be a list"]
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            errors.append(f"{rel}: action {index + 1} must be an object")
            continue
        for field in ("id", "type", "title"):
            if field not in action:
                errors.append(f"{rel}: action {index + 1} missing field: {field}")
        action_type = action.get("type")
        if action_type not in ALLOWED_CHANGE_ACTION_TYPES:
            errors.append(f"{rel}: action {action.get('id', index + 1)} has unsupported type: {action_type}")
        if action_type == "git_config":
            for field in ("key", "value"):
                if field not in action:
                    errors.append(f"{rel}: git_config action {action.get('id', index + 1)} missing {field}")
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
