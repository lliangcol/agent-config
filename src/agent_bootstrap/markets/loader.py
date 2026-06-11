from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_bootstrap.core.policy import load_yaml_file


def load_marketplace(path: str | Path) -> dict[str, Any]:
    data = load_yaml_file(path)
    if not isinstance(data, dict):
        raise ValueError(f"marketplace must be an object: {path}")
    return data


def load_marketplaces(paths: list[str | Path], base_dir: Path | None = None) -> list[dict[str, Any]]:
    marketplaces = []
    for path in paths:
        candidate = Path(path)
        if not candidate.is_absolute() and base_dir is not None:
            candidate = base_dir / candidate
        marketplaces.append(load_marketplace(candidate))
    return marketplaces
