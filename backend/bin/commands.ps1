#!/usr/bin/env pwsh
$ErrorActionPreference = 'Stop'

if ($args.Count -eq 0) {
    $command = ''
} else {
    $command = $args[0]
    $rest = if ($args.Count -gt 1) { $args[1..($args.Count - 1)] } else { @() }
}

switch ($command) {
    'migrate' {
        Write-Host 'Running migrations...'
        & alembic upgrade head
    }
    'downgrade' {
        $revision = if ($rest.Count -gt 0) { $rest[0] } else { '-1' }
        Write-Host "Downgrading to: $revision"
        & alembic downgrade $revision
    }
    'generate' {
        $migrationName = "migration_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Write-Host "Generating migration: $migrationName"
        & alembic revision --autogenerate -m $migrationName
    }
    'seed' {
        Write-Host 'Running seeders...'
        & python -m app.database.seeders.run
    }
    'test' {
        Write-Host 'Running pytest...'
        & pytest ./tests/ @rest
    }
    'reset' {
        Write-Host 'Clearing ./data ...'
        if (Test-Path ./data) {
            Get-ChildItem -Path ./data -Force | Remove-Item -Recurse -Force
        }
        New-Item -ItemType Directory -Force -Path ./data | Out-Null
        Write-Host 'Running migrations...'
        & alembic upgrade head
        Write-Host 'Running seeders...'
        & python -m app.database.seeders.run
    }
    default {
        Write-Host "Unknown command: $command"
        Write-Host ''
        Write-Host 'Usage: bin/commands.ps1 <command>'
        Write-Host ''
        Write-Host 'Commands:'
        Write-Host '  migrate              Apply all pending migrations'
        Write-Host '  downgrade [rev]      Downgrade one step, or pass a revision to go to a specific one'
        Write-Host '  generate             Auto-generate a new migration from model changes'
        Write-Host '  seed                 Run all seeders'
        Write-Host '  test [args...]       Run pytest (extra args forwarded)'
        Write-Host '  reset                Delete ./data, then migrate + seed (destructive)'
        exit 1
    }
}

exit $LASTEXITCODE
