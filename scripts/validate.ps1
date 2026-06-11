Set-StrictMode -Version 3.0
$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root
$env:PYTHONPATH = (Join-Path $Root "src")
$env:PYTHONDONTWRITEBYTECODE = "1"

function Resolve-Python {
  foreach ($candidate in @("python", "python3", "py")) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($null -eq $cmd) {
      continue
    }
    if ($candidate -eq "py") {
      & py -3 -c "import sys; print(sys.version)" | Out-Null
      if ($LASTEXITCODE -eq 0) {
        return "py"
      }
    } else {
      & $candidate -c "import sys; print(sys.version)" | Out-Null
      if ($LASTEXITCODE -eq 0) {
        return $candidate
      }
    }
  }
  throw "Python 3 is required for validation"
}

$script:PythonLauncher = Resolve-Python

function Invoke-Python {
  param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments)
  if ($script:PythonLauncher -eq "py") {
    & py -3 @Arguments
  } else {
    & $script:PythonLauncher @Arguments
  }
  if ($LASTEXITCODE -ne 0) {
    throw "Python command failed: $($Arguments -join ' ')"
  }
}

function Step {
  param([Parameter(Mandatory=$true)][string]$Name, [Parameter(Mandatory=$true)][scriptblock]$Body)
  Write-Output "==> $Name"
  & $Body
}

Step "Python syntax check" {
  Invoke-Python @("-c", "import ast, pathlib; paths=[p for root in ['src','tests','scripts','skills'] for p in pathlib.Path(root).rglob('*.py')]; [ast.parse(p.read_text(encoding='utf-8'), filename=str(p)) for p in paths]; print(f'python syntax ok: {len(paths)}')")
}

Step "pytest" {
  Invoke-Python @("-m", "pytest", "-q", "-p", "no:cacheprovider")
}

Step "JSON schemas load" {
  Invoke-Python @("-c", "import json, pathlib; [json.loads(p.read_text(encoding='utf-8')) for p in pathlib.Path('schemas').glob('*.json')]; print('schemas ok')")
}

Step "YAML configs load" {
  Invoke-Python @("-c", "from pathlib import Path; from agent_bootstrap.core.policy import load_yaml_file; paths=list(Path('config').glob('**/*.yaml')); [load_yaml_file(p) for p in paths]; print(f'configs ok: {len(paths)}')")
}

Step "Config shapes" {
  Invoke-Python @("scripts/validate-config-shapes.py")
}

Step "CLI smoke audit" {
  Invoke-Python @("-m", "agent_bootstrap", "audit", "--profile", "config/profiles/default.yaml", "--agent", "generic", "--format", "json") | Out-Null
}

Step "CLI smoke plan" {
  Invoke-Python @("-m", "agent_bootstrap", "plan", "--profile", "config/profiles/default.yaml", "--agent", "generic", "--format", "markdown") | Out-Null
}

Step "CLI smoke verify" {
  Invoke-Python @("-m", "agent_bootstrap", "verify", "--profile", "config/profiles/default.yaml", "--agent", "generic", "--format", "json") | Out-Null
}

Step "CLI smoke apply dry-run" {
  Invoke-Python @("-m", "agent_bootstrap", "apply", "--change-set", "config/change-sets/windows-dev-safe.example.yaml", "--format", "json") | Out-Null
}

Step "Skill frontmatter" {
  Invoke-Python @("-c", "from pathlib import Path; text=Path('skills/agent-capability-bootstrap-audit/SKILL.md').read_text(encoding='utf-8'); assert text.startswith('---\n'); head=text.split('---',2)[1]; assert 'name:' in head and 'description:' in head; print('skill frontmatter ok')")
}

Step "Skill assets" {
  Invoke-Python @("scripts/sync-skill-assets.py", "--check")
}

Write-Output "validation ok"
