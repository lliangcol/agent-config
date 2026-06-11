# New Machine Bootstrap

Start with OS-level basics before Agent-specific checks. The Windows workstation baseline is Windows 11 plus WSL2 Ubuntu 24.04 as the primary development environment.

1. Run the matching bootstrap script in `bootstrap/`.
2. Review Git, SSH, Node.js, Python, WinGet/Scoop strategy, WSL2, Docker, PATH, proxy, and GitHub reachability status.
3. Run `python skills/agent-capability-bootstrap-audit/scripts/audit-agent-capabilities.py audit --profile config/profiles/default.yaml --format markdown` from this source repository.
4. Review risks and missing items.
5. Generate an install plan only after confirming the target Agent with `--agent codex`, `--agent claude-code`, or `--agent generic`.
6. Use `apply` only for explicit host configuration changes from a structured change-set file:
   `python skills/agent-capability-bootstrap-audit/scripts/audit-agent-capabilities.py apply --change-set config/change-sets/windows-dev-safe.example.yaml --format markdown`.
7. To execute allowlisted host configuration changes, rerun with `--confirm EXECUTE_HOST_CHANGES` after reviewing the dry-run output.

The bootstrap scripts print next steps but do not install tools. `apply` blocks package installs, login flows, plugin installation, MCP registration, and arbitrary shell commands.
