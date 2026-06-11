# Custom Marketplaces Reference

Supported config fields:

- `agent`: `codex`, `claude-code`, or `generic`
- `source.type`: `official`, `github`, `git`, `url`, or `local`
- `trust.level`: `official`, `organization`, `personal`, `third-party`, or `unknown`
- `policy.default_mode`: `audit-only`, `plan-install`, or `execute-after-confirm`

Rules:

- `official` can be recommended and can enter `plan-install`.
- `organization` and `personal` can generate plans but require user confirmation.
- `third-party` and `unknown` remain `audit-only` by default.
- Unpinned `github`, `git`, and `url` sources must be marked risky and blocked from install planning.
- Validation commands must be listed in the plan when provided by the marketplace config.
