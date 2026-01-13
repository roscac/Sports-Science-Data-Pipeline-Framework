"""Bootstrap a local .venv and install dependencies."""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from scripts.helpers.logging_utils import get_logger

def _run(cmd, cwd: Path):
    subprocess.check_call(cmd, cwd=str(cwd))

def setup(project_root: Path, configure_vscode: bool = True) -> None:
    """Create a virtual environment and install project requirements."""
    project_root = project_root.resolve()
    log = get_logger(project_root, "setup")
    venv_dir = project_root / ".venv"
    python_exec = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python_exec.exists():
        log.info("Creating virtual environment (.venv)...")
        _run([sys.executable, "-m", "venv", str(venv_dir)], project_root)
    log.info("Installing dependencies...")
    req = project_root / "requirements.txt"
    if req.exists():
        _run([str(python_exec), "-m", "pip", "install", "--upgrade", "pip"], project_root)
        _run([str(python_exec), "-m", "pip", "install", "-r", str(req)], project_root)
    if configure_vscode:
        vscode = project_root / ".vscode"
        vscode.mkdir(exist_ok=True)
        settings = vscode / "settings.json"
        interp = "${workspaceFolder}\\.venv\\Scripts\\python.exe" if os.name == "nt" else "${workspaceFolder}/.venv/bin/python"
        settings.write_text('{' + f'\n  "python.defaultInterpreterPath": "{interp}",\n  "python.terminal.activateEnvironment": true\n' + '}\n')
        log.info("VS Code workspace configured.")
    log.info("Setup complete.")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--no-vscode", action="store_true")
    args = ap.parse_args()
    setup(Path(args.project_root), configure_vscode=not args.no_vscode)
