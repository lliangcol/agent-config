from __future__ import annotations

from pathlib import Path


def find_git_root_by_filesystem(cwd: Path) -> Path | None:
    current = cwd.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def project_path(cwd: Path, relative: str) -> Path:
    return cwd / relative
