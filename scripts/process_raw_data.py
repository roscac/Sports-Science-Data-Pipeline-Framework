"""Vendor-aware raw data processing into anonymized ML inputs."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd

from scripts.helpers.vendor_adapters import detect_vendor, load_catapult_csv, load_vald_forcedecks_csv
from scripts.anonymize import anonymize_dataframe, write_identity_key
from scripts.qc_checks import run_basic_qc
from scripts.helpers.logging_utils import get_logger

def process_raw_folder(project_root: Path, raw_folder: Path) -> Path:
    """Load raw vendor CSVs, run QC, anonymize, and write ml_input output."""
    log = get_logger(project_root, "processing")
    raw_folder = raw_folder.resolve()
    files = [p for p in raw_folder.iterdir() if p.is_file() and p.suffix.lower()==".csv"]
    if not files:
        raise FileNotFoundError(f"No CSV files found in {raw_folder}")

    vendor = detect_vendor(files)
    frames = []
    warnings = []
    for f in files:
        if vendor == "catapult":
            res = load_catapult_csv(f)
        elif vendor == "vald_forcedecks":
            res = load_vald_forcedecks_csv(f)
        else:
            df = pd.read_csv(f)
            df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
            res = type("R", (), {"df": df, "warnings": ("Generic loader used; add adapter for better results.",)})
        frames.append(res.df)
        warnings.extend(list(res.warnings))

    df = pd.concat(frames, ignore_index=True)
    for w in warnings:
        log.warning(w)

    for msg in run_basic_qc(df):
        log.info(f"QC: {msg}")

    anon = anonymize_dataframe(df, project_root)
    for w in anon.warnings:
        log.warning(w)

    if not anon.key_df.empty:
        key_path = write_identity_key(anon.key_df, project_root)
        log.info(f"Identity key updated at: {key_path}")

    out_dir = project_root / "data" / "ml_input"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"{vendor}_ml_input_{ts}.csv"
    anon.df.to_csv(out_path, index=False)
    log.info(f"Wrote ML input dataset: {out_path}")
    return out_path
