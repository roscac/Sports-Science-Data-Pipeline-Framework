"""Export a sanitized project snapshot without sensitive folders."""
from __future__ import annotations
from pathlib import Path
import shutil
from scripts.helpers.logging_utils import get_logger

def export_project(project_root: Path, export_dest: Path) -> Path:
    """Copy a safe project replica, excluding local-only directories."""
    log = get_logger(project_root, "export")
    project_root = project_root.resolve()
    export_dest = export_dest.resolve()
    export_dest.mkdir(parents=True, exist_ok=True)

    def should_skip(rel: Path) -> bool:
        rel_str = str(rel).replace("\\", "/")
        return rel_str.startswith("data/raw/") or rel_str.startswith("data/identity_key/") or rel_str.startswith("data/upload/") or rel_str.startswith("logs/")

    for src in project_root.rglob("*"):
        if src.is_dir():
            continue
        rel = src.relative_to(project_root)
        if should_skip(rel):
            continue
        dst = export_dest / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    for p in [export_dest/"data/raw", export_dest/"data/identity_key", export_dest/"data/upload", export_dest/"logs"]:
        p.mkdir(parents=True, exist_ok=True)

    log.info(f"Export complete: {export_dest}")
    return export_dest
