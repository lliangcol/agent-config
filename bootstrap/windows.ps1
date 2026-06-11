Set-StrictMode -Version 3.0

function Test-CommandAvailable {
  param([Parameter(Mandatory=$true)][string]$Name)
  $cmd = Get-Command $Name -ErrorAction SilentlyContinue
  if ($null -eq $cmd) {
    Write-Output "[missing] $Name"
  } else {
    Write-Output "[ok] $Name -> $($cmd.Source)"
  }
}

Write-Output "Agent capability bootstrap preflight (Windows)"
Write-Output "OS: $([System.Environment]::OSVersion.VersionString)"
Write-Output "Shell: PowerShell $($PSVersionTable.PSVersion)"
Write-Output "Architecture: $([System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture)"
Write-Output "PATH entries: $(($env:PATH -split ';' | Where-Object { $_ }).Count)"

Test-CommandAvailable git
Test-CommandAvailable ssh
Test-CommandAvailable node
Test-CommandAvailable npm
Test-CommandAvailable pnpm
Test-CommandAvailable python
Test-CommandAvailable py
Test-CommandAvailable uv
Test-CommandAvailable volta
Test-CommandAvailable winget
Test-CommandAvailable scoop
Test-CommandAvailable choco
Test-CommandAvailable wsl
Test-CommandAvailable docker
Test-CommandAvailable claude
Test-CommandAvailable codex
Test-CommandAvailable code
Test-CommandAvailable zed

foreach ($name in @("git", "ssh", "volta", "node", "npm", "pnpm", "uv", "python", "claude", "codex", "docker")) {
  $resolved = Get-Command $name -ErrorAction SilentlyContinue
  if ($null -ne $resolved) {
    Write-Output "[path] $name -> $($resolved.Source)"
  }
}

if (Get-Command wsl -ErrorAction SilentlyContinue) {
  Write-Output ""
  Write-Output "WSL distributions:"
  wsl -l -v
}

Write-Output ""
Write-Output "Proxy environment:"
foreach ($name in @("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy")) {
  $value = [Environment]::GetEnvironmentVariable($name)
  if ([string]::IsNullOrWhiteSpace($value)) {
    Write-Output "[proxy] $name=<unset>"
  } else {
    Write-Output "[proxy] $name=$value"
  }
}

if (Get-Command Test-NetConnection -ErrorAction SilentlyContinue) {
  $github = Test-NetConnection github.com -Port 443 -WarningAction SilentlyContinue
  if ($github.TcpTestSucceeded) {
    Write-Output "[ok] github.com:443 reachable"
  } else {
    Write-Output "[warn] github.com:443 not confirmed"
  }
} else {
  Write-Output "[warn] Test-NetConnection unavailable; manually verify github.com:443"
}

Write-Output ""
Write-Output "Next steps:"
Write-Output "1. Review missing tools."
Write-Output "2. Run: python skills/agent-capability-bootstrap-audit/scripts/audit-agent-capabilities.py audit --profile config/profiles/default.yaml --format markdown"
Write-Output "3. Dry-run host configuration changes with: python -m agent_bootstrap apply --change-set config/change-sets/windows-dev-safe.example.yaml --format markdown"
Write-Output "4. Do not install anything until the generated plan is reviewed and confirmed."
