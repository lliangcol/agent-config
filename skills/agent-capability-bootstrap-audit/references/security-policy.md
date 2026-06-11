# Security Policy

Never perform these actions in audit mode:

- System package installation.
- Agent plugin installation.
- Skill projection into runtime directories.
- MCP server registration.
- Login, OAuth, device authorization, or credential helper changes.
- Shell commands that mutate user or project configuration.

The `apply` command is the only execution path for host configuration changes. It must:

- Dry-run by default.
- Require `--confirm EXECUTE_HOST_CHANGES` for mutation.
- Execute only structured allowlisted action types.
- Block package installation, login flows, plugin installation, MCP registration, and arbitrary shell commands.
- Block placeholder values such as `<...>` or `你的邮箱`.

Every recommendation must include:

- Detection command or inspected path.
- Found value or missing status.
- Reason the item is missing or risky.
- Suggested action.
- Verification command.

`execute-after-confirm` is represented as a future mode. In v1, it must produce blocked actions and confirmation requirements, not real execution.
