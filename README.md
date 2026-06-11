# agent-capability-bootstrap-audit

Audit AI agent workstation capabilities and generate confirmation-gated install plans.

This repository is audit-first by design. The default workflow gathers evidence about a machine, an agent runtime, and configured capability marketplaces. It does not install packages, perform login flows, install plugins, register MCP servers, or run arbitrary shell commands.

## What It Does

- Audits Codex, Claude Code, or generic agent environments.
- Checks base workstation capabilities such as Git, SSH, runtimes, package managers, WSL, Docker, and GitHub reachability.
- Loads trusted marketplace metadata and profile policies from `config/`.
- Produces Markdown or JSON audit reports and install plans.
- Supports a separate `apply` flow for a narrow allowlist of host configuration actions after an explicit confirmation token.

## Safety Model

`audit`, `plan`, and `verify` are read-only workflows. `apply` is dry-run by default and only executes allowlisted structured actions when passed `--confirm EXECUTE_HOST_CHANGES`.

Allowed host action types are:

- `git_config`
- `powershell_execution_policy`
- `user_env`

Blocked action types include package installs, agent login/install flows, plugin installs, MCP registration, and arbitrary shell commands.

## Quick Start From Source

Requirements:

- Python 3.11 or newer
- `pytest` for the validation gate

Run a read-only audit from a source checkout:

```powershell
python skills/agent-capability-bootstrap-audit/scripts/audit-agent-capabilities.py audit --profile config/profiles/default.yaml --format markdown
```

Generate a plan after selecting an agent target:

```powershell
python skills/agent-capability-bootstrap-audit/scripts/audit-agent-capabilities.py plan --profile config/profiles/default.yaml --agent codex --format markdown
```

Dry-run an allowlisted host configuration change set:

```powershell
python skills/agent-capability-bootstrap-audit/scripts/audit-agent-capabilities.py apply --change-set config/change-sets/windows-dev-safe.example.yaml --format markdown
```

If the package is installed in a Python environment, the equivalent console command is `agent-bootstrap`.

## Validation

Run the platform validation gate before submitting changes.

Windows:

```powershell
.\scripts\validate.ps1
```

Unix-like systems:

```bash
bash scripts/validate.sh
```

The gate performs Python syntax checks, unit tests, schema/config loading, config shape validation, CLI smoke tests, and skill asset checks.

## Repository Layout

- `src/agent_bootstrap/` - CLI, detectors, policy logic, renderers, and confirmation-gated apply logic.
- `skills/agent-capability-bootstrap-audit/` - source skill package and references.
- `config/` - profiles, policy files, marketplaces, and example change sets.
- `schemas/` - JSON schemas for reports, plans, marketplaces, profiles, and change sets.
- `docs/` - architecture, marketplace policy, bootstrap notes, and decisions.
- `tests/` - unit and smoke tests.

## Project Status

The project is in an early `0.1.x` stage. Interfaces and schemas are intended to be stable enough for source-based use, but users should review generated plans manually and keep host changes confirmation-gated.
