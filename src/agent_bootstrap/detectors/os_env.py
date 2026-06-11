from __future__ import annotations

import os
import platform


def detect_os_shell_arch() -> tuple[str, str, str]:
    system = platform.system() or "unknown"
    shell = os.environ.get("SHELL") or os.environ.get("COMSPEC") or os.environ.get("ComSpec") or "unknown"
    arch = platform.machine() or platform.processor() or "unknown"
    return system, shell, arch


def path_entries() -> list[str]:
    return [entry for entry in os.environ.get("PATH", "").split(os.pathsep) if entry]
