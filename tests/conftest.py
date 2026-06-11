from __future__ import annotations

from collections.abc import Sequence

from agent_bootstrap.core.model import Evidence
import pytest


class FakeRunner:
    def __init__(self, available: set[str] | None = None, outputs: dict[tuple[str, ...], str] | None = None):
        self.available = available or set()
        self.outputs = outputs or {}
        self.calls: list[tuple[str, ...]] = []

    def which(self, command: str) -> str | None:
        return f"/fake/bin/{command}" if command in self.available else None

    def run(self, args: Sequence[str], timeout: int = 10) -> Evidence:
        args_tuple = tuple(args)
        self.calls.append(args_tuple)
        command = " ".join(args)
        if not args or args[0] not in self.available:
            return Evidence(command, "", "missing", f"{args[0]} not found in PATH", command)
        value = self.outputs.get(args_tuple, f"{args[0]} ok")
        return Evidence(command, value, "ok", "command exited with 0", command)


@pytest.fixture
def fake_runner_factory():
    def factory(available: set[str], outputs: dict[tuple[str, ...], str] | None = None) -> FakeRunner:
        return FakeRunner(available=available, outputs=outputs)

    return factory
