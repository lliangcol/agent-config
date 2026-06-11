# Win11 WSL Workstation Capability Expansion Plan

## Source Of Truth

- Baseline document: `D:\Work\Resources\Config\Develop\Windows11_开发环境重装配置说明.md`
- Repository rules: default remains `audit-only`; real installs, login flows, plugin installation, MCP registration, and system package installation remain disallowed by default.

## Draft Plan

1. Extend audit output beyond `git/node/python` into workstation capability groups:
   - Windows base and package manager strategy.
   - Git and SSH.
   - WSL2 Ubuntu 24.04.
   - Windows and WSL Node toolchains.
   - Windows and WSL Python/uv toolchains.
   - WSL Java and Maven.
   - Docker Desktop and WSL Docker CLI.
   - IDE, proxy, backup advisory checks.
2. Add profile metadata for the Win11 + WSL2 target:
   - WinGet required.
   - Scoop optional helper.
   - Chocolatey optional/non-default.
   - Windows Node through Volta, WSL Node through fnm, Node major 22.
   - Python through uv, Python major/minor 3.12.
   - WSL distro `Ubuntu-24.04`.
3. Add confirmation-gated execution capability:
   - Add an `apply` CLI command.
   - Default to dry-run unless `--confirm EXECUTE_HOST_CHANGES` is supplied.
   - Execute only allowlisted structured host configuration actions, not arbitrary plan text.
   - Block package installs, login/auth flows, plugin installs, MCP registration, and unknown action types.
4. Add a sample change-set file:
   - Safe git global config actions from the baseline, excluding personal email placeholders.
   - PowerShell execution policy as an explicit, confirmation-gated action.
5. Update renderers, schemas, validation, references, and tests.

## Review Pass 1

Findings:

- P1: The draft plan does not clearly separate audit-only checks from execution actions; this can weaken the repository safety model.
- P1: "Full workstation coverage" can become too broad if every IDE/VPN/database installation is treated as required. The baseline distinguishes core development stack from advisory desktop tools.
- P1: Execution must not run `winget`, `scoop`, `apt`, `curl | sh`, `claude`, `codex`, login, plugin, or MCP commands. The plan must encode those as blocked by policy.
- P2: Profile metadata needs to drive output, but the existing v1 schema and tests should remain backward compatible.
- P2: WSL checks must tolerate machines without WSL installed and report evidence rather than fail the audit.
- P2: Docker checks must avoid pulling images or starting containers.

## Fixed Plan

1. Preserve the current `audit/plan/verify` behavior and add fields rather than replacing v1 output:
   - Add `AuditResult.capabilities`.
   - Keep existing `tools`, `package_managers`, `network`, and adapter fields for compatibility.
2. Implement workstation audit as evidence-backed, read-only capability groups:
   - `windows_base`: PowerShell, WinGet, execution policy, PATH advisory.
   - `git_ssh`: Git, OpenSSH, GitHub SSH probe, global Git config keys.
   - `wsl`: `wsl -l -v`, Ubuntu-24.04 presence, WSL version evidence.
   - `node_toolchain`: Windows Volta/node/npm/pnpm and WSL fnm/node/npm/pnpm.
   - `python_toolchain`: Windows uv/python and WSL uv/python.
   - `java_toolchain`: WSL java/javac/mvn.
   - `docker`: Windows docker, Docker Compose, WSL docker, WSL Docker Compose.
   - `ide`: code, zed, and advisory IntelliJ evidence.
   - `network_proxy`: proxy environment and Git/npm proxy config evidence.
   - `backup`: important backup path existence evidence.
3. Treat optional tools correctly:
   - WinGet missing is high risk on Windows.
   - Scoop missing is low-risk optional.
   - Chocolatey missing is informational and not a default repair recommendation.
4. Add execution as a separate `apply` command:
   - `agent-bootstrap apply --change-set <path> --format json|markdown`
   - Dry-run by default.
   - Real mutation requires `--confirm EXECUTE_HOST_CHANGES`.
   - Allowlisted actions: `git_config`, `powershell_execution_policy`, `user_env`.
   - Blocked actions: package managers, agent login/install, plugin install, MCP registration, arbitrary shell.
   - Placeholder values such as `<...>` and `你的邮箱` are blocked.
5. Add an example change set under `config/change-sets/` for baseline-safe host config changes.
6. Update docs and skill references to document the new audit and apply boundaries.
7. Validate with focused tests plus `.\scripts\validate.ps1`.

## Re-review

Verdict: ready to implement.

Residual risks accepted:

- WSL and Docker probes may return environment-specific errors; they must be represented as evidence, not test failures.
- The `apply` command introduces real host mutation capability only when explicitly confirmed. Full install automation remains intentionally blocked.
- IDE/VPN/backup coverage is advisory and should not block workstation readiness unless future profiles mark it required.
