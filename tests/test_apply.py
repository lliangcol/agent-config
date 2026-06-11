from __future__ import annotations

from pathlib import Path

from agent_bootstrap.core.apply import CONFIRM_TOKEN, apply_change_set


def test_apply_change_set_dry_run_skips_allowlisted_actions(tmp_path, fake_runner_factory):
    change_set = tmp_path / "changes.yaml"
    change_set.write_text(
        '{"name":"demo","actions":[{"id":"branch","type":"git_config","title":"branch","key":"init.defaultBranch","value":"main"}]}',
        encoding="utf-8",
    )
    runner = fake_runner_factory({"git"})

    result = apply_change_set(change_set, runner)

    assert result.dry_run is True
    assert len(result.skipped) == 1
    assert result.skipped[0].command == "git config --global init.defaultBranch main"
    assert runner.calls == []


def test_apply_change_set_executes_when_confirmed(tmp_path, fake_runner_factory):
    change_set = tmp_path / "changes.yaml"
    change_set.write_text(
        '{"name":"demo","actions":[{"id":"branch","type":"git_config","title":"branch","key":"init.defaultBranch","value":"main"}]}',
        encoding="utf-8",
    )
    runner = fake_runner_factory({"git"})

    result = apply_change_set(change_set, runner, confirm=CONFIRM_TOKEN)

    assert result.dry_run is False
    assert len(result.executed) == 1
    assert runner.calls == [("git", "config", "--global", "init.defaultBranch", "main")]


def test_apply_change_set_blocks_unsafe_and_placeholder_actions(tmp_path, fake_runner_factory):
    change_set = tmp_path / "changes.yaml"
    change_set.write_text(
        """
{
  "name": "demo",
  "actions": [
    {"id":"install","type":"winget_install","title":"install git"},
    {"id":"email","type":"git_config","title":"email","key":"user.email","value":"你的邮箱"}
  ]
}
""",
        encoding="utf-8",
    )
    runner = fake_runner_factory({"git", "winget"})

    result = apply_change_set(change_set, runner, confirm=CONFIRM_TOKEN)

    assert [item.id for item in result.blocked] == ["install", "email"]
    assert result.executed == []
