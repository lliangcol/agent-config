# Environment Bootstrap Reference

Audit these machine basics first:

- OS, shell, CPU architecture, PATH length.
- Git with `git --version`.
- SSH with `ssh -V` and GitHub SSH with `ssh -T git@github.com`.
- Node.js with `node --version`.
- Python with `python --version`, `python3 --version`, or `py --version`.
- Package managers by OS: Windows `winget` is preferred, `scoop` is optional for helper CLIs, and `choco` is advisory only; macOS `brew`; Linux `apt`, `dnf`, `yum`, `pacman`, `apk`, `zypper`.
- Windows workstation baseline: WSL2 Ubuntu 24.04, Windows Volta + Node.js 22 + pnpm, WSL fnm + Node.js 22 + pnpm, uv + Python 3.12 on both Windows and WSL.
- WSL development baseline: Git, OpenJDK 17, Maven, uv, Node.js, pnpm, Docker CLI, Claude Code, and Codex.
- Docker Desktop baseline: WSL2 backend enabled and Docker Compose available; do not pull images or start containers during audit.
- GitHub reachability via HTTPS or TCP 443.
- Proxy or DNS suspicion when GitHub is unreachable but local commands exist.

Bootstrap scripts must only report status and next commands. They must not install packages and must not require Python.

Host configuration changes belong in explicit `apply` change sets. `apply` must dry-run by default and require `--confirm EXECUTE_HOST_CHANGES` before running allowlisted actions.
