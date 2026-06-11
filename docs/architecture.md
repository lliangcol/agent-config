# Architecture

`agent-capability-bootstrap-audit` is an audit-first toolkit for new machines and AI Agent environments. Its default mode is read-only audit and confirmation-gated planning. A separate `apply` flow can execute a small allowlist of structured host configuration changes only when the user supplies the required confirmation token.

The package is split into small layers:

- `detectors/` collect OS, runtime, package manager, network, and repository evidence.
- `adapters/` apply Agent-specific read-only rules for Codex, Claude Code, or generic fallback.
- `markets/` load and validate marketplace metadata.
- `core/` owns evidence models, policy decisions, and install plan generation.
- `core/apply.py` owns confirmation-gated host configuration execution for allowlisted action types.
- `renderers/` produce stable Markdown and JSON output.
- `installers/` contain plan-only helpers and never perform installation.

The CLI always starts from an audit. `plan` converts audit evidence plus marketplace policy into confirmation-gated actions. `verify` reruns the same read-only checks after the user performs any external setup. `apply` executes only structured actions such as `git_config`, `powershell_execution_policy`, and `user_env`; package installation, login, plugin installation, MCP registration, and arbitrary shell remain blocked.
