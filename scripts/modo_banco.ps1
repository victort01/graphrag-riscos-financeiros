param([ValidateSet('ingestao','consulta')][string]$Modo = 'consulta')
$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    $env:NEO4J_READ_ONLY = if ($Modo -eq 'consulta') { 'true' } else { 'false' }
    & docker compose up -d
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao iniciar o banco.' }
    $pronto = $false
    for ($tentativa = 0; $tentativa -lt 60; $tentativa++) {
        try {
            $resposta = Invoke-WebRequest 'http://127.0.0.1:17474' -UseBasicParsing -TimeoutSec 2
            if ($resposta.StatusCode -eq 200) { $pronto = $true; break }
        } catch { Start-Sleep -Seconds 1 }
    }
    if (-not $pronto) { throw 'O banco não respondeu. Consulte docker compose logs neo4j.' }
    Write-Output "Banco pronto no modo $Modo."
} finally {
    Remove-Item Env:NEO4J_READ_ONLY -ErrorAction SilentlyContinue
    Pop-Location
}
