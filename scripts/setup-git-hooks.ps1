# Run once after cloning (PowerShell): wires up the repo's tracked Git hooks.
git config core.hooksPath .githooks
Write-Host "core.hooksPath set to .githooks (pre-push will run ruff + pytest)"
