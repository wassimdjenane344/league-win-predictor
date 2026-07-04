#!/usr/bin/env bash
# Run once after cloning: wires up the repo's tracked Git hooks.
set -e
git config core.hooksPath .githooks
chmod +x .githooks/pre-push
echo "core.hooksPath set to .githooks (pre-push will run ruff + pytest)"
