#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src"
export PYTHONDONTWRITEBYTECODE=1

if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "Python 3 is required for validation" >&2
  exit 1
fi

step() {
  echo "==> $1"
  shift
  "$@"
}

step "Python syntax check" "$PYTHON" -c "import ast, pathlib; paths=[p for root in ['src','tests','scripts','skills'] for p in pathlib.Path(root).rglob('*.py')]; [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in paths]; print(f'python syntax ok: {len(paths)}')"
step "pytest" "$PYTHON" -m pytest -q -p no:cacheprovider
step "JSON schemas load" "$PYTHON" -c "import json, pathlib; [json.loads(p.read_text(encoding='utf-8')) for p in pathlib.Path('schemas').glob('*.json')]; print('schemas ok')"
step "Project metadata load" "$PYTHON" -c "import pathlib, tomllib; data=tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8')); assert data['project']['name'] == 'agent-capability-bootstrap-audit'; print('pyproject ok')"
step "YAML configs load" "$PYTHON" -c "from pathlib import Path; from agent_bootstrap.core.policy import load_yaml_file; paths=list(Path('config').glob('**/*.yaml')); [load_yaml_file(p) for p in paths]; print(f'configs ok: {len(paths)}')"
step "Config shapes" "$PYTHON" scripts/validate-config-shapes.py
step "CLI smoke audit" "$PYTHON" -m agent_bootstrap audit --profile config/profiles/default.yaml --agent generic --format json
step "CLI smoke plan" "$PYTHON" -m agent_bootstrap plan --profile config/profiles/default.yaml --agent generic --format markdown
step "CLI smoke verify" "$PYTHON" -m agent_bootstrap verify --profile config/profiles/default.yaml --agent generic --format json
step "CLI smoke apply dry-run" "$PYTHON" -m agent_bootstrap apply --change-set config/change-sets/windows-dev-safe.example.yaml --format json
step "Skill frontmatter" "$PYTHON" -c "from pathlib import Path; text=Path('skills/agent-capability-bootstrap-audit/SKILL.md').read_text(encoding='utf-8'); assert text.startswith('---\n'); head=text.split('---',2)[1]; assert 'name:' in head and 'description:' in head; print('skill frontmatter ok')"
step "Skill assets" "$PYTHON" scripts/sync-skill-assets.py --check
echo "validation ok"
