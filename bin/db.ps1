#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'
& docker compose exec backend bin/db @args
exit $LASTEXITCODE
