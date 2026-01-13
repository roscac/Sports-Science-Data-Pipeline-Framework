"""Re-identify ML outputs using the local identity key."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd
from scripts.helpers.logging_utils import get_logger

def load_identity_key(project_root: Path) -> pd.DataFrame:
    """Load the local identity key mapping anon_id -> athlete_name."""
    key_path = project_root / "data" / "identity_key" / "identity_key.csv"
    if not key_path.exists():
        raise FileNotFoundError(f"Identity key not found at {key_path}. Add it before re-identification.")
    key = pd.read_csv(key_path)
    if "anon_id" not in key.columns or "athlete_name" not in key.columns:
        raise ValueError("Identity key must contain columns: anon_id, athlete_name")
    return key

def reidentify_files(project_root: Path, ml_project_name: str, files: list[Path]) -> Path:
    """Merge identity key into ML outputs and write a local upload CSV."""
    log = get_logger(project_root, "reidentify")
    key = load_identity_key(project_root)
    out_dir = project_root / "data" / "upload"
    out_dir.mkdir(parents=True, exist_ok=True)
    dfs = []
    for f in files:
        df = pd.read_csv(f)
        df = df.merge(key, how="left", left_on="athlete_id", right_on="anon_id")
        df.drop(columns=["anon_id"], inplace=True, errors="ignore")
        dfs.append(df)
        log.info(f"Re-identified: {f.name}")
    out_df = pd.concat(dfs, ignore_index=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"teamworks_upload_{ml_project_name}_{ts}.csv"
    out_df.to_csv(out_path, index=False)
    log.info(f"Wrote upload file: {out_path}")
    return out_path
