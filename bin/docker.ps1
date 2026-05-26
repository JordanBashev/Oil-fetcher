#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'
& docker compose exec backend bin/commands @args
exit $LASTEXITCODE
