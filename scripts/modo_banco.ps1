param([ValidateSet('ingestao','consulta')][string]$Modo = 'consulta')
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    $env:NEO4J_READ_ONLY = if ($Modo -eq 'consulta') { 'true' } else { 'false' }
    & docker compose up -d
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao iniciar o banco.' }
    $pythonRiscos = Join-Path (Get-Location).Path '.venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $pythonRiscos)) { $pythonRiscos = 'python' }
    & $pythonRiscos scripts/aguardar_banco.py
    if ($LASTEXITCODE -ne 0) { throw 'O banco nao ficou pronto. Consulte docker compose logs neo4j.' }
    Write-Output "Banco pronto no modo $Modo."
} finally {
    Remove-Item Env:NEO4J_READ_ONLY -ErrorAction SilentlyContinue
    Pop-Location
}
