"""CLI anonymization pass for raw CSVs into ml_input."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from scripts.anonymize import anonymize_dataframe, write_identity_key
from scripts.helpers.logging_utils import get_logger


def anonymize_raw_folder(project_root: Path, raw_folder: Path) -> Path:
    """Anonymize raw CSVs and write a merged ml_input CSV."""
    log = get_logger(project_root, "anonymize_raw")
    raw_folder = raw_folder.resolve()
    files = [p for p in raw_folder.iterdir() if p.is_file() and p.suffix.lower() == ".csv"]
    if not files:
        raise FileNotFoundError(f"No CSV files found in {raw_folder}")

    frames: list[pd.DataFrame] = []
    for f in files:
        df = pd.read_csv(f)
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
        frames.append(df)

    df = pd.concat(frames, ignore_index=True)
    anon = anonymize_dataframe(df, project_root)
    for w in anon.warnings:
        log.warning(w)

    if not anon.key_df.empty:
        key_path = write_identity_key(anon.key_df, project_root)
        log.info(f"Identity key updated at: {key_path}")

    out_dir = project_root / "data" / "ml_input"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"raw_ml_input_{ts}.csv"
    anon.df.to_csv(out_path, index=False)
    log.info(f"Wrote ML input dataset: {out_path}")
    return out_path


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", default=".")
    ap.add_argument("--raw-folder", default="data/raw")
    args = ap.parse_args()
    anonymize_raw_folder(Path(args.project_root), Path(args.raw_folder))
