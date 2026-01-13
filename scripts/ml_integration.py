"""Stub ML pipeline for portfolio demonstration."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import pandas as pd
from scripts.helpers.logging_utils import get_logger

def run_model_pipeline(project_root: Path, ml_project_name: str, ml_input_files: list[Path]) -> list[Path]:
    """Read ML inputs and emit model outputs to the project outputs folder."""
    log = get_logger(project_root, "ml_run")
    out_dir = project_root / "ml_models" / ml_project_name / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for f in ml_input_files:
        df = pd.read_csv(f)
        df["model_processed"] = True
        df["model_version"] = "v1"
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        out_path = out_dir / f"{f.stem}_model_output_{ts}.csv"
        df.to_csv(out_path, index=False)
        outputs.append(out_path)
        log.info(f"Wrote ML output: {out_path}")
    return outputs
