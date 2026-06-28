# -*- mode: python ; coding: utf-8 -*-
# PT: Spec do PyInstaller para empacotar a GUI CORA em executavel unico. | EN: PyInstaller spec for packaging the CORA GUI as a single executable.

from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules
from pathlib import Path

# PT: Coleta dados e imports dinamicos necessarios para execucao no executavel. | EN: Collects data and dynamic imports required by the executable.
project_root = Path(SPECPATH)
app_icon = project_root / 'Logo_GIM_02.ico'
app_icon_png = project_root / 'Logo_GIM_02_icon.png'

datas = [
    (str(app_icon_png), '.'),
    (str(app_icon), '.'),
]
hiddenimports = ['threadpoolctl', 'matplotlib.backends.backend_tkagg']
datas += collect_data_files('matplotlib')
hiddenimports += collect_submodules('sklearn')


a = Analysis(
    ['cora_projeto/run_cora_gui.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# PT: EXE sem console, apropriado para aplicacao desktop tkinter. | EN: Console-free EXE suitable for the Tkinter desktop application.
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CORA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(app_icon),
)
