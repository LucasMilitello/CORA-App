param(
    [string]$Folder,
    [string]$Output
)

Set-Location -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Python do ambiente virtual nao encontrado: $venvPython"
}

$appArgs = @("-m", "cora_projeto.qt.init_qt")
if ($Folder) {
    $appArgs += "--folder"
    $appArgs += $Folder
}
if ($Output) {
    $appArgs += "--output"
    $appArgs += $Output
}

& $venvPython @appArgs
