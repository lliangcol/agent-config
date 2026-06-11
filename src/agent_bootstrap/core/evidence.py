from __future__ import annotations

import os
import shutil
import socket
import subprocess
from pathlib import Path, PureWindowsPath
from typing import Iterable, Sequence

from .model import Evidence


def display_command(args: Sequence[str]) -> str:
    return " ".join(_quote_display_arg(arg) for arg in args)


def _quote_display_arg(arg: str) -> str:
    if not arg:
        return '""'
    if any(ch.isspace() for ch in arg):
        return '"' + arg.replace('"', '\\"') + '"'
    return arg


def trim_output(value: str, limit: int = 600) -> str:
    clean = " ".join(value.strip().split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3] + "..."


class CommandRunner:
    def which(self, command: str) -> str | None:
        return shutil.which(command)

    def run(self, args: Sequence[str], timeout: int = 10) -> Evidence:
        command_text = display_command(args)
        if not args:
            return Evidence(command_text, "", "error", "empty command", command_text)
        resolved_command = self.which(args[0])
        if resolved_command is None:
            return Evidence(command_text, "", "missing", f"{args[0]} not found in PATH", command_text)
        invocation, prepare_error = self._prepare_invocation(args, resolved_command)
        if prepare_error:
            return Evidence(command_text, "", "error", prepare_error, command_text)
        try:
            completed = subprocess.run(
                invocation,
                capture_output=True,
                check=False,
                encoding="utf-8",
                errors="replace",
                shell=False,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return Evidence(command_text, "", "error", f"command timed out after {timeout}s", command_text)
        except OSError as exc:
            return Evidence(command_text, "", "error", str(exc), command_text)
        output = trim_output(completed.stdout or completed.stderr)
        if completed.returncode == 0:
            return Evidence(command_text, output, "ok", "command exited with 0", command_text)
        return Evidence(
            command_text,
            output,
            "error",
            f"command exited with {completed.returncode}",
            command_text,
        )

    def _prepare_invocation(self, args: Sequence[str], resolved_command: str) -> tuple[list[str], str | None]:
        if _is_windows_host() and PureWindowsPath(resolved_command).suffix.lower() == ".ps1":
            powershell = self.which("pwsh") or self.which("powershell")
            if powershell is None:
                return [], "PowerShell not found; cannot execute Windows .ps1 command shim"
            return [
                powershell,
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                resolved_command,
                *args[1:],
            ], None
        return [resolved_command, *args[1:]], None


def command_finding(command: str, args: Sequence[str], runner: CommandRunner) -> Evidence:
    return runner.run(args)


def path_evidence(path: Path, label: str) -> Evidence:
    expanded = path.expanduser()
    exists = expanded.exists()
    return Evidence(
        command=f"inspect {label}",
        value=str(path),
        status="ok" if exists else "missing",
        reason="path exists" if exists else "path not found",
        verify_command=path_verify_command(path),
    )


def path_verify_command(path: Path) -> str:
    if _is_windows_host():
        return f"Test-Path -LiteralPath {_quote_powershell_literal(str(path))}"
    return f"test -e {_quote_posix_literal(str(path))}"


def _is_windows_host() -> bool:
    return os.name == "nt"


def _quote_powershell_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _quote_posix_literal(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def tcp_evidence(host: str, port: int, timeout: float = 3.0) -> Evidence:
    command = f"tcp {host}:{port}"
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return Evidence(command, f"{host}:{port}", "ok", "TCP connection succeeded", command)
    except OSError as exc:
        return Evidence(command, f"{host}:{port}", "warn", str(exc), command)


def present_evidence(label: str, value: str, verify_command: str) -> Evidence:
    return Evidence(label, value, "ok", "detected", verify_command)


def missing_evidence(label: str, value: str, reason: str, verify_command: str) -> Evidence:
    return Evidence(label, value, "missing", reason, verify_command)


def summarize_status(evidence: Iterable[Evidence]) -> str:
    statuses = [item.status for item in evidence]
    if any(status == "ok" for status in statuses):
        return "ok"
    if any(status == "warn" for status in statuses):
        return "warn"
    if any(status == "error" for status in statuses):
        return "error"
    return "missing"
