"""Qt GUI entrypoint for the pipeline demo."""
from __future__ import annotations
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path for package imports when launched via -m or direct script.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def _maybe_reexec_in_venv() -> None:
    # Auto-reexec into the local .venv so GUI deps resolve without manual activation.
    if os.environ.get("SSDP_VENV_REEXEC"):
        return
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if in_venv:
        return
    venv_python = PROJECT_ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if venv_python.exists():
        os.environ["SSDP_VENV_REEXEC"] = "1"
        os.execv(str(venv_python), [str(venv_python), __file__] + sys.argv[1:])

_maybe_reexec_in_venv()
try:
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QLabel,
        QPushButton,
        QFileDialog,
        QCheckBox,
        QGroupBox,
        QHBoxLayout,
        QInputDialog,
        QMessageBox,
    )
    from PySide6.QtCore import Qt
    _PYSIDE6_IMPORT_ERROR = None
except ModuleNotFoundError as exc:
    _PYSIDE6_IMPORT_ERROR = exc
    QApplication = QMainWindow = QWidget = QVBoxLayout = QLabel = QPushButton = QFileDialog = QCheckBox = object
    QGroupBox = QHBoxLayout = QInputDialog = QMessageBox = object

    class _QtDummy:
        Checked = 2

    Qt = _QtDummy()

from gui.status_panel import StatusPanel
from scripts.process_raw_data import process_raw_folder
from scripts.ml_integration import run_model_pipeline
from scripts.reidentify import reidentify_files
from scripts.export_project import export_project

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sports Science Pipeline")
        self.project_root = Path(".").resolve()
        self.ml_project_name = "example_model"
        self.advanced = False

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        title = QLabel("Sports Science Pipeline")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.chk_adv = QCheckBox("Advanced Mode")
        self.chk_adv.toggled.connect(self._toggle_adv)
        layout.addWidget(self.chk_adv)

        btn_process = QPushButton("Process Raw Data (data/raw -> data/ml_input)")
        btn_process.clicked.connect(self._process_raw)
        layout.addWidget(btn_process)

        btn_run = QPushButton("Run ML Project (ml_input -> ml_models/<project>/outputs)")
        btn_run.clicked.connect(self._run_ml)
        layout.addWidget(btn_run)

        btn_reid = QPushButton("Re-identify for Upload (select ML outputs)")
        btn_reid.clicked.connect(self._reidentify)
        layout.addWidget(btn_reid)

        self.advanced_group = QGroupBox("Advanced Tools")
        adv_layout = QVBoxLayout()
        self.advanced_group.setLayout(adv_layout)

        btn_row = QHBoxLayout()
        self.btn_git_status = QPushButton("Git Status")
        self.btn_git_status.clicked.connect(self._git_status)
        btn_row.addWidget(self.btn_git_status)

        self.btn_git_pull = QPushButton("Git Pull")
        self.btn_git_pull.clicked.connect(self._git_pull)
        btn_row.addWidget(self.btn_git_pull)

        self.btn_git_push = QPushButton("Git Push")
        self.btn_git_push.clicked.connect(self._git_push)
        btn_row.addWidget(self.btn_git_push)

        adv_layout.addLayout(btn_row)

        self.btn_git_commit = QPushButton("Git Commit (stage all)")
        self.btn_git_commit.clicked.connect(self._git_commit)
        adv_layout.addWidget(self.btn_git_commit)

        self.chk_auto_delete = QCheckBox("Auto-delete selected ML outputs after re-identify")
        adv_layout.addWidget(self.chk_auto_delete)

        self.btn_export = QPushButton("Export Project (replica minus sensitive files)")
        self.btn_export.clicked.connect(self._export)
        adv_layout.addWidget(self.btn_export)

        self.advanced_group.setVisible(False)
        layout.addWidget(self.advanced_group)

        self.status = StatusPanel()
        layout.addWidget(self.status)

    def _toggle_adv(self, checked: bool):
        """Show/hide advanced tools and update state."""
        self.advanced = bool(checked)
        self.advanced_group.setVisible(self.advanced)
        for w in [
            self.btn_git_status,
            self.btn_git_commit,
            self.btn_git_pull,
            self.btn_git_push,
            self.chk_auto_delete,
            self.btn_export,
        ]:
            w.setEnabled(self.advanced)
        self.status.log(f"Mode: {'Advanced' if self.advanced else 'Beginner'}")

    def _process_raw(self):
        """Run vendor processing on data/raw and write ml_input output."""
        try:
            out = process_raw_folder(self.project_root, self.project_root / "data" / "raw")
            self.status.log(f"Created ML input: {out}")
        except Exception as e:
            self.status.log(f"ERROR processing raw: {e}")

    def _run_ml(self):
        """Run the ML stub on current ml_input CSVs."""
        ml_input_dir = self.project_root / "data" / "ml_input"
        files = sorted(list(ml_input_dir.glob("*.csv")))
        if not files:
            self.status.log("No ml_input files found. Run Process Raw Data first.")
            return
        try:
            outs = run_model_pipeline(self.project_root, self.ml_project_name, files)
            self.status.log(f"Wrote {len(outs)} ML output file(s) to ml_models/{self.ml_project_name}/outputs/")
        except Exception as e:
            self.status.log(f"ERROR running ML: {e}")

    def _reidentify(self):
        """Re-identify selected ML output CSVs for upload."""
        outputs_dir = self.project_root / "ml_models" / self.ml_project_name / "outputs"
        if not outputs_dir.exists():
            self.status.log(f"Outputs folder missing: {outputs_dir}")
            return
        selected, _ = QFileDialog.getOpenFileNames(self, "Select ML output file(s)", str(outputs_dir), "CSV Files (*.csv)")
        if not selected:
            self.status.log("No files selected.")
            return
        try:
            out = reidentify_files(self.project_root, self.ml_project_name, [Path(p) for p in selected])
            self.status.log(f"Created upload file: {out}")
            if self.advanced and self.chk_auto_delete.isChecked():
                for p in selected:
                    path = Path(p)
                    if path.exists():
                        path.unlink()
                        self.status.log(f"Deleted ML output: {path.name}")
            if not self.advanced:
                self.status.log("Beginner mode: auto-delete after successful upload is expected (API upload not included yet).")
        except Exception as e:
            self.status.log(f"ERROR re-identifying: {e}")

    def _export(self):
        """Export a sanitized project replica to a user-selected destination."""
        dest = QFileDialog.getExistingDirectory(self, "Choose export destination")
        if not dest:
            return
        export_dest = Path(dest) / "project_export"
        try:
            export_project(self.project_root, export_dest)
            self.status.log(f"Exported to: {export_dest}")
        except Exception as e:
            self.status.log(f"ERROR exporting: {e}")

    def _get_repo(self):
        """Return a GitPython Repo handle or None if unavailable."""
        try:
            from git import Repo, InvalidGitRepositoryError, NoSuchPathError
        except Exception as e:
            self.status.log(f"ERROR loading GitPython: {e}")
            return None
        try:
            return Repo(self.project_root, search_parent_directories=True)
        except (InvalidGitRepositoryError, NoSuchPathError) as e:
            self.status.log(f"ERROR: not a git repo ({e})")
            return None

    def _git_status(self):
        """Log `git status --short` output."""
        repo = self._get_repo()
        if not repo:
            return
        try:
            status = repo.git.status("--short")
            if not status.strip():
                self.status.log("Git status: clean")
            else:
                self.status.log("Git status:\n" + status)
        except Exception as e:
            self.status.log(f"ERROR git status: {e}")

    def _git_pull(self):
        """Pull latest changes from the current branch."""
        repo = self._get_repo()
        if not repo:
            return
        try:
            out = repo.git.pull()
            self.status.log(f"Git pull: {out}")
        except Exception as e:
            self.status.log(f"ERROR git pull: {e}")

    def _git_push(self):
        """Push current branch to its remote."""
        repo = self._get_repo()
        if not repo:
            return
        try:
            out = repo.git.push()
            self.status.log(f"Git push: {out}")
        except Exception as e:
            self.status.log(f"ERROR git push: {e}")

    def _git_commit(self):
        """Stage all changes and commit with a user message."""
        repo = self._get_repo()
        if not repo:
            return
        try:
            if not repo.is_dirty(untracked_files=True):
                self.status.log("Git commit: no changes to commit.")
                return
            msg, ok = QInputDialog.getText(self, "Commit Message", "Enter commit message:")
            if not ok or not msg.strip():
                self.status.log("Git commit canceled.")
                return
            repo.git.add(A=True)
            commit = repo.index.commit(msg.strip())
            self.status.log(f"Git commit: {commit.hexsha[:7]} {msg.strip()}")
        except Exception as e:
            self.status.log(f"ERROR git commit: {e}")

def main():
    if _PYSIDE6_IMPORT_ERROR:
        sys.stderr.write(
            "PySide6 is required to run the GUI.\n"
            "Run `python scripts/first_time_setup.py` or install dependencies with "
            "`python -m pip install -r requirements.txt` inside the project.\n"
        )
        raise SystemExit(1)
    app = QApplication([])
    w = MainWindow()
    w.resize(900, 600)
    w.show()
    app.exec()

if __name__ == "__main__":
    main()
