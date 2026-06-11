#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    src = repo_root / "src"
    if src.exists():
        sys.path.insert(0, str(src))
    try:
        from agent_bootstrap.cli import main as cli_main
    except ImportError as exc:
        print(f"agent_bootstrap package is not importable: {exc}", file=sys.stderr)
        print("Run from the source repository or install the package first.", file=sys.stderr)
        return 2
    return cli_main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
