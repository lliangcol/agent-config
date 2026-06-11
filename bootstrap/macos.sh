#!/usr/bin/env bash
set -u

check_command() {
  name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    printf '[ok] %s -> %s\n' "$name" "$(command -v "$name")"
  else
    printf '[missing] %s\n' "$name"
  fi
}

echo "Agent capability bootstrap preflight (macOS)"
echo "OS: $(uname -s)"
echo "Shell: ${SHELL:-unknown}"
echo "Architecture: $(uname -m)"
printf 'PATH entries: %s\n' "$(printf '%s' "${PATH:-}" | tr ':' '\n' | sed '/^$/d' | wc -l | tr -d ' ')"

check_command git
check_command node
check_command python3
check_command python
check_command brew
check_command port

if command -v nc >/dev/null 2>&1 && nc -z -w 3 github.com 443 >/dev/null 2>&1; then
  echo "[ok] github.com:443 reachable"
elif command -v curl >/dev/null 2>&1 && curl -I --max-time 5 https://github.com >/dev/null 2>&1; then
  echo "[ok] github.com reachable over HTTPS"
else
  echo "[warn] github.com connectivity not confirmed"
fi

echo
echo "Next steps:"
echo "1. Review missing tools."
echo "2. Run: python3 skills/agent-capability-bootstrap-audit/scripts/audit-agent-capabilities.py audit --profile config/profiles/default.yaml --format markdown"
echo "3. Do not install anything until the generated plan is reviewed and confirmed."
