param([string]$Compilador = '')
$ErrorActionPreference = 'Stop'
$repoArtigo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$pastaFerramentasArtigo = Join-Path $repoArtigo 'data/tools/tectonic'
if (-not $Compilador) {
    $Compilador = Join-Path $pastaFerramentasArtigo 'tectonic.exe'
    if (-not (Test-Path -LiteralPath $Compilador)) {
        New-Item -ItemType Directory -Force -Path $pastaFerramentasArtigo | Out-Null
        $arquivoZipArtigo = Join-Path $repoArtigo 'data/tools/tectonic.zip'
        Invoke-WebRequest -Uri 'https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/tectonic-0.17.0-x86_64-pc-windows-msvc.zip' -OutFile $arquivoZipArtigo
        $hashZipArtigo = (Get-FileHash -LiteralPath $arquivoZipArtigo -Algorithm SHA256).Hash.ToLower()
        if ($hashZipArtigo -ne 'f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f') {
            throw 'Checksum do compilador divergente; arquivo nao executado.'
        }
        Expand-Archive -LiteralPath $arquivoZipArtigo -DestinationPath $pastaFerramentasArtigo
    }
}
$hashClasseArtigo = (Get-FileHash -LiteralPath (Join-Path $PSScriptRoot 'IEEEtran.cls') -Algorithm SHA256).Hash.ToLower()
if ($hashClasseArtigo -ne 'da751920a317ed318b7b5cd7fa585a6cc7d28502d457856382e9be24b10a3bd7') {
    throw 'A classe IEEEtran difere da copia original registrada.'
}
$saidaArtigo = Join-Path $PSScriptRoot '.build'
New-Item -ItemType Directory -Force -Path $saidaArtigo | Out-Null
& $Compilador -X compile (Join-Path $PSScriptRoot 'artigo-revisao.tex') --outdir $saidaArtigo --keep-logs
if ($LASTEXITCODE -ne 0) { throw 'A compilacao falhou. Consulte o log em .build.' }
Write-Output 'PDF de trabalho gerado em docs/artigo/.build. Revise antes de atualizar a entrega.'
