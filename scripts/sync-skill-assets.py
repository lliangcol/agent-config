#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/codex-adapter.md",
    "references/claude-code-adapter.md",
    "references/environment-bootstrap.md",
    "references/custom-marketplaces.md",
    "references/security-policy.md",
    "scripts/audit-agent-capabilities.py",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate skill source assets without runtime projection.")
    parser.add_argument("--check", action="store_true", help="Validate skill source files.")
    parser.add_argument("--write", action="store_true", help="No-op in this project; runtime projection is intentionally disabled.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    skill_root = root / "skills" / "agent-capability-bootstrap-audit"
    missing = [path for path in REQUIRED if not (skill_root / path).exists()]
    if missing:
        for path in missing:
            print(f"missing skill asset: {path}")
        return 1
    if args.write:
        print("runtime projection is disabled; source skill assets are already in skills/.")
    else:
        print("skill assets ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
