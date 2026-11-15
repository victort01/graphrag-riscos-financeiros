param(
    [string]$Servidor = (Join-Path $PSScriptRoot '../data/models/llama/llama-server.exe'),
    [string]$Modelo = (Join-Path $PSScriptRoot '../data/models/qwen2.5-1.5b-instruct-q4_k_m.gguf')
)
$ErrorActionPreference = 'Stop'
$executavel = (Resolve-Path -LiteralPath $Servidor).Path
$arquivoModelo = (Resolve-Path -LiteralPath $Modelo).Path
& $executavel --model $arquivoModelo --alias qwen-riscos-local --host 127.0.0.1 --port 18081 --ctx-size 4096 --threads 4 --parallel 1 --batch-size 128
exit $LASTEXITCODE
