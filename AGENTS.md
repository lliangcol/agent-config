# Agent Config Repository Instructions

This repository contains the source package for `agent-capability-bootstrap-audit`.

## Operating Rules

- Default behavior is `audit-only`.
- Do not perform real installs, login flows, authorization, plugin installation, MCP registration, or system package installation.
- Generate evidence-backed audit reports and confirmation-gated install plans by default.
- Host configuration execution, when implemented or tested, must be an explicit `apply` flow with structured allowlisted actions and an unmistakable confirmation token. It must not execute package installs, login flows, plugin installation, MCP registration, or arbitrary shell commands.
- Keep `skills/agent-capability-bootstrap-audit/` as the source skill package. Do not project it automatically into Codex `.agents/skills` or Claude Code `.claude/skills`.
- Treat local machine paths, installed plugins, installed skills, and versions as runtime evidence or test fixtures only. Never encode them as general defaults.
- Keep deterministic logic in `src/` or `skills/*/scripts/`; keep long guidance in `references/`; keep `SKILL.md` concise.

## Validation

Run the Windows validation gate before handoff:

```powershell
.\scripts\validate.ps1
```

On Unix-like systems:

```bash
./scripts/validate.sh
```
