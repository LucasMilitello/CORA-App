# Developer Manual

This document provides a basic technical guide for developers who want to understand, run, modify, test, or package CORA.

## 1. Project Overview

CORA is a Python desktop application for wound-healing image analysis. The application loads microscopy images, groups them by experiment and time point, runs an image-processing segmentation pipeline, allows visual review of masks, and exports measurement results.

The main production interface is currently based on Tkinter. The repository also contains an experimental PySide6/Qt interface.

## 2. Main Technologies

- Python: main programming language.
- Tkinter: main desktop user interface.
- PySide6: experimental Qt interface.
- NumPy, SciPy, OpenCV, scikit-learn, tifffile: image-processing and analysis stack.
- Matplotlib: visualization support.
- Pillow: image/icon handling.
- PyInstaller: Windows executable packaging.

## 3. Repository Layout

```text
cora_projeto/
  cora_interface.py              Main Tkinter application window and workflow
  matlab_style_cora.py           Core image-processing and segmentation pipeline
  run_cora_gui.py                Main application entry point
  guia_teoria_interface.txt      Technical/usage notes

cora_projeto/services/
  grouping_service.py            Image discovery and grouping logic
  processing_service.py          Processing orchestration and worker logic
  export_service.py              Export helpers for results and spreadsheets

cora_projeto/pages/
  main_page.py                   Main Tkinter layout
  roi_page.py                    ROI editor page helpers

cora_projeto/qt/
  init_qt.py                     Experimental Qt entry point
  cora_interface_qt.py           Experimental Qt main window
  core/                          Tkinter-compatible logic reused by Qt
  ui/                            Qt widgets and dialogs

tools/
  make_app_icon.py               Generates icon assets for packaging

CORA_testes/
  Optional development workspace for robotized and performance tests

requirements.txt                 Main runtime dependencies
CORA.spec                        PyInstaller specification
build_exe.ps1                    Windows build script
build_exe.bat                    Windows build wrapper
launch-qt.ps1                    Helper script for the Qt interface
README.md                        User-facing project documentation
```

## 4. Local Development Setup

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the main application:

```powershell
python -m cora_projeto.run_cora_gui
```

Run the experimental Qt interface:

```powershell
python -m cora_projeto.qt.init_qt
```

## 5. Application Entry Points

### Main Tkinter App

```powershell
python -m cora_projeto.run_cora_gui
```

This entry point performs a lightweight environment check and then loads the main Tkinter application from `cora_projeto.cora_interface`.

### Tkinter Compatibility Entry Point

```powershell
python -m cora_projeto.tk.run_cora_gui
```

This is a smaller compatibility wrapper for launching the Tkinter application.

### Experimental Qt App

```powershell
python -m cora_projeto.qt.init_qt
```

The Qt interface is experimental and may not expose every feature available in the Tkinter application.

## 6. Processing Flow

At a high level, the application follows this workflow:

1. The user selects an image folder.
2. `grouping_service.py` scans files and groups images by experiment/time point.
3. The UI displays detected groups and lets the user confirm or adjust inputs.
4. `processing_service.py` runs the segmentation pipeline for each selected image.
5. `matlab_style_cora.py` performs the image-processing operations and returns masks, overlays, and area results.
6. The user reviews results and optionally edits masks/ROIs.
7. `export_service.py` writes results and output files.

## 7. Generated Output

When no custom output folder is selected, the application may create:

```text
_cora_resultados/
```

Temporary processing files may be created under:

```text
.cora_tmp/
```

These directories are runtime outputs and should not be committed to Git.

## 8. Build Process

The Windows executable is generated with PyInstaller.

Run:

```powershell
.\build_exe.ps1 -Clean
```

The build script:

1. Checks that the selected Python installation has a working Tcl/Tk runtime.
2. Installs missing build dependencies when needed.
3. Generates icon assets using `tools/make_app_icon.py`.
4. Runs PyInstaller with `CORA.spec`.
5. Writes the executable to `dist/CORA.exe`.

Important build assets:

```text
Logo_GIM_02.png
Logo_GIM_02_icon.png
Logo_GIM_02.ico
CORA.spec
tools/make_app_icon.py
```

## 9. Test Workspace

The `CORA_testes/` folder contains optional development and robotized test utilities.

It includes:

- Robotized tests using `pywinauto`.
- Performance/reporting helpers.
- A test-oriented copy of the application package.
- Extra dependencies in `requirements_robotizado.txt`.

Install robotized test dependencies:

```powershell
python -m pip install -r CORA_testes\requirements_robotizado.txt
```

Some robotized tests depend on local Windows paths and local test images. Before running them on another machine, review and update the paths inside the test scripts.

## 10. Git Versioning Rules

Commit source files, documentation, configuration, scripts, and required image/icon assets.

Do commit:

```text
README.md
DEVELOPER_MANUAL.md
.gitignore
requirements.txt
cora_projeto/
tools/
CORA.spec
build_exe.ps1
build_exe.bat
launch-qt.ps1
Logo_GIM_02.png
Logo_GIM_02_icon.png
Logo_GIM_02.ico
```

Optionally commit:

```text
CORA_testes/
.vscode/
Logo_GIM.ico
Logo_GIM_semfundo.png
```

Do not commit:

```text
.venv/
__pycache__/
build/
dist/
.cora_tmp/
_cora_resultados/
*.zip
*.log
```

## 11. Development Guidelines

- Keep application logic in `services/` when it is not directly tied to UI rendering.
- Keep UI-specific code in `cora_interface.py`, `pages/`, or `qt/ui/`.
- Keep the core segmentation pipeline in `matlab_style_cora.py`.
- Avoid hard-coded absolute paths in production code.
- Do not commit generated results, virtual environments, caches, or packaged executables.
- Update `requirements.txt` when adding a new runtime dependency.
- Update this manual when changing entry points, build steps, or project structure.

## 12. Common Commands

Run the main app:

```powershell
python -m cora_projeto.run_cora_gui
```

Run the Qt app:

```powershell
python -m cora_projeto.qt.init_qt
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Build the executable:

```powershell
.\build_exe.ps1 -Clean
```

Generate icon assets manually:

```powershell
python tools\make_app_icon.py --source Logo_GIM_02.png --png Logo_GIM_02_icon.png --ico Logo_GIM_02.ico
```

## 13. Known Notes

- The Tkinter interface is the most complete interface.
- The Qt interface is experimental.
- The test workspace may require local path adjustments.
- The repository currently has no license file. Add a `LICENSE` file before public distribution if usage rights need to be defined.
