---
name: agent-capability-bootstrap-audit
description: Audit a new computer or AI Agent environment for Codex or Claude Code plugins, skills, MCP servers, configuration docs, custom marketplaces, base runtimes, and confirmation-gated install plans. Use for new machines, Agent configuration audits, Codex/Claude Code capability bootstrap, marketplace trust review, and plugin/skill/MCP recommendations.
---

# Agent Capability Bootstrap Audit

Use this skill to audit and plan by default. Use `apply` only for explicit, structured, confirmation-gated host configuration changes.

## Workflow

1. Identify the current Agent: Codex, Claude Code, or generic fallback.
2. Read the user profile and marketplace config.
3. Run `audit-only` first:
   `python skills/agent-capability-bootstrap-audit/scripts/audit-agent-capabilities.py audit --profile config/profiles/default.yaml --format markdown`
4. Report missing items, recommendations, evidence commands, risks, and actions that need confirmation.
5. Wait for explicit user confirmation before generating an install plan.
6. After confirmation, generate a plan only:
   `python skills/agent-capability-bootstrap-audit/scripts/audit-agent-capabilities.py plan --agent <codex|claude-code|generic> --format markdown`
7. After any user-performed installation, run `verify-only`:
   `python skills/agent-capability-bootstrap-audit/scripts/audit-agent-capabilities.py verify --agent <codex|claude-code|generic> --format markdown`
8. For host configuration changes, dry-run a structured change set first:
   `python skills/agent-capability-bootstrap-audit/scripts/audit-agent-capabilities.py apply --change-set config/change-sets/windows-dev-safe.example.yaml --format markdown`
9. Execute only after explicit confirmation:
   `python skills/agent-capability-bootstrap-audit/scripts/audit-agent-capabilities.py apply --change-set <path> --confirm EXECUTE_HOST_CHANGES --format markdown`

`apply` must not install packages, perform login flows, install plugins, register MCP servers, or run arbitrary shell commands.

## References

- Codex behavior: `references/codex-adapter.md`
- Claude Code behavior: `references/claude-code-adapter.md`
- Base machine checks: `references/environment-bootstrap.md`
- Custom marketplace trust: `references/custom-marketplaces.md`
- Security policy: `references/security-policy.md`

Do not copy this skill into `.agents/skills` or `.claude/skills` unless the user explicitly asks to install it.
