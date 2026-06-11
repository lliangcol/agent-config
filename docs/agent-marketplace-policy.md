# Agent Marketplace Policy

Marketplaces are treated as trusted code distribution channels.

- Official marketplaces may be recommended and planned.
- Organization and personal marketplaces require explicit confirmation before planning install actions.
- Third-party and unknown marketplaces remain audit-only by default.
- GitHub, git, and URL sources must be pinned before they can enter install planning.
- Validation commands are carried into generated plans and must be run by the user or a separate confirmed workflow.

Codex and Claude Code rules are not interchangeable. The CLI selects one adapter at a time and falls back to generic mode when the current Agent is ambiguous.
