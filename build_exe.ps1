param(
    [string]$Python = "python",
    [switch]$Clean
)

# PT: Interrompe o script no primeiro erro para evitar build parcial. | EN: Stops the script on the first error to prevent a partial build.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Test-BuildPython {
    param([string]$Candidate)

    $probe = & $Candidate -c "import tkinter as tk; tk.Tcl().eval('info patchlevel')" 2>&1
    return ($LASTEXITCODE -eq 0)
}

# PT: Limpeza opcional para gerar build totalmente novo. | EN: Optional cleanup to generate a completely fresh build.
if ($Clean) {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "build", "dist"
}

if (-not (Test-BuildPython $Python)) {
    throw "O Python selecionado nao tem Tcl/Tk funcional para empacotar o CORA. Use, por exemplo: .\build_exe.ps1 -Python `"C:\Program Files\Python313\python.exe`""
}

$logoSourcePath = Join-Path $root "Logo_GIM_02.png"
$iconPngPath = Join-Path $root "Logo_GIM_02_icon.png"
$iconPath = Join-Path $root "Logo_GIM_02.ico"
if (-not (Test-Path $logoSourcePath)) {
    throw "Logo nao encontrado: $logoSourcePath"
}

# PT: Instala somente dependencias ausentes para o build Tkinter. PySide6 nao e necessario para o CORA.exe. | EN: Installs only missing dependencies for the Tkinter build. PySide6 is not required for CORA.exe.
$missingDeps = & $Python -c "import importlib.util; mods=['PyInstaller','PIL','cv2','matplotlib','numpy','scipy','sklearn','tifffile','threadpoolctl']; print('\n'.join(m for m in mods if importlib.util.find_spec(m) is None))"
if ($LASTEXITCODE -ne 0) {
    throw "Falha ao verificar dependencias do Python selecionado."
}
$missingDeps = @($missingDeps | Where-Object { $_ })
if ($missingDeps.Count -gt 0) {
    $buildRequirements = Join-Path $env:TEMP "cora-build-requirements.txt"
    Get-Content requirements.txt |
        Where-Object { $_.Trim() -and ($_ -notmatch '^\s*PySide6\b') } |
        Set-Content -Encoding ASCII $buildRequirements
    & $Python -m pip install -r $buildRequirements pyinstaller
} else {
    Write-Host "Dependencias de build ja encontradas."
}

# PT: Gera icone quadrado a partir da Logo_GIM_02 para evitar corte/distorcao no Windows. | EN: Generates a square icon from Logo_GIM_02 to avoid Windows clipping/distortion.
& $Python tools\make_app_icon.py --source $logoSourcePath --png $iconPngPath --ico $iconPath
if (-not (Test-Path $iconPath)) {
    throw "Icone nao gerado: $iconPath"
}
if (-not (Test-Path $iconPngPath)) {
    throw "PNG do icone nao gerado: $iconPngPath"
}

# PT: Empacota a GUI em arquivo unico (sem console) usando o spec com icone e recursos. | EN: Packages the GUI as a single file (without a console) using the spec with icon and resources.
& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    CORA.spec

Write-Host ""
Write-Host "Build concluido: dist\\CORA.exe"

