param([int]$Porta = 18501)
$ErrorActionPreference = 'Stop'
$raizRiscos = Split-Path -Parent $PSScriptRoot
$pythonRiscos = Join-Path $raizRiscos '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $pythonRiscos)) { throw 'Prepare o ambiente .venv conforme o README.' }
Push-Location $raizRiscos
try {
    & $pythonRiscos -m streamlit run app.py --server.address 127.0.0.1 --server.port $Porta --server.headless true --browser.gatherUsageStats false
    exit $LASTEXITCODE
} finally { Pop-Location }
