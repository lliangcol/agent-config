# Claude Code Adapter Reference

Official source URLs:

- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/plugins
- https://code.claude.com/docs/en/discover-plugins
- https://code.claude.com/docs/en/plugin-marketplaces
- https://code.claude.com/docs/en/plugins-reference
- https://code.claude.com/docs/en/mcp

Implementation rules:

- Detect the CLI with `claude --version`.
- Inspect personal skills at `~/.claude/skills` and project skills at `.claude/skills`.
- Inspect `.claude/settings.json`, `.claude/settings.local.json`, `.mcp.json`, and `~/.claude.json` read-only.
- Detect plugin inventory with `claude plugin list --json`.
- Detect marketplaces with `claude plugin marketplace list --json`.
- Support official marketplace naming: `claude-plugins-official` and source `anthropics/claude-plugins-official`.
- Include `claude plugin validate .` as a validation command only.
- Include `/reload-plugins` as a post-install user prompt only.
- Claude plugins can include skills, commands, agents, hooks, MCP servers, LSP servers, monitors, settings, and executable bins.
- Do not run plugin install, marketplace add, MCP add, login, or update commands in audit mode.
