# Codex Adapter Reference

Official source URLs:

- https://developers.openai.com/codex/skills
- https://developers.openai.com/codex/plugins
- https://developers.openai.com/codex/plugins/build
- https://developers.openai.com/codex/mcp
- https://developers.openai.com/codex/config-basic

Implementation rules:

- Detect the CLI with `codex --version`.
- Inspect user config at `~/.codex/config.toml` and project config at `.codex/config.toml` read-only.
- Detect plugin and marketplace commands with `codex plugin marketplace list` and `codex plugin list`.
- Detect MCP support with `codex mcp --help`.
- Discover skill directories dynamically. Codex repo skills live under `.agents/skills`; user skills live under `$HOME/.agents/skills`; admin/system skills are only summarized when visible.
- Treat plugins, skills, MCP servers, and app connectors as separate recommendation kinds.
- Do not run `codex plugin install`, `codex plugin marketplace add`, `codex mcp add`, `codex mcp login`, or any auth command in audit mode.
