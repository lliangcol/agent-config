# Contributing

Thank you for considering a contribution.

## Development Rules

- Preserve the audit-first default. Do not add package installs, login flows, plugin installation, MCP registration, or arbitrary shell execution to default workflows.
- Keep real host mutation inside explicit `apply` flows with structured allowlisted actions and the `EXECUTE_HOST_CHANGES` confirmation token.
- Do not encode local machine paths, private configuration, installed plugin versions, or personal environment assumptions as general defaults.
- Keep deterministic logic in `src/` or `skills/*/scripts/`; keep long guidance in `references/`; keep `SKILL.md` concise.
- Add or update tests when changing CLI behavior, policy decisions, schemas, renderers, or host action handling.

## Local Validation

Run the validation gate before opening a pull request.

Windows:

```powershell
.\scripts\validate.ps1
```

Unix-like systems:

```bash
bash scripts/validate.sh
```

Also check the staged diff before committing:

```bash
git diff --cached --check
```

## Pull Requests

Use a concise title and include:

- What changed.
- Why it changed.
- Which validation commands passed.
- Any safety or compatibility impact.
