from __future__ import annotations

import json
from typing import Any

from agent_bootstrap.core.model import to_dict


def render_json(value: Any) -> str:
    return json.dumps(to_dict(value), ensure_ascii=True, indent=2, sort_keys=True)
