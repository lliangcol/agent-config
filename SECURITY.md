# Security Policy

## Supported Versions

Until the first stable release, security fixes are handled on the latest `main` branch and the current `0.1.x` line.

## Reporting A Vulnerability

Do not include secrets, tokens, private host paths, or full audit reports in public issues. Use GitHub private vulnerability reporting when it is enabled for the repository. If private reporting is not available, contact the repository owner through a non-public channel and include only the minimum reproduction details needed to investigate.

## Security Expectations

- Default commands must remain read-only.
- Generated plans must be reviewed before use.
- Host configuration changes must remain dry-run by default.
- Execution must require `--confirm EXECUTE_HOST_CHANGES`.
- Package installs, login flows, plugin installs, MCP registration, and arbitrary shell execution must remain blocked by policy.
