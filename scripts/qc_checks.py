"""Minimal QC checks for demo dataframes."""
from __future__ import annotations
from typing import List
import pandas as pd

def run_basic_qc(df: pd.DataFrame) -> List[str]:
    """Return human-readable QC messages for required columns."""
    msgs: List[str] = []
    msgs.append(f"rows={len(df):,} cols={len(df.columns):,}")
    required = ["athlete_id", "datetime_utc", "session_id"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        msgs.append(f"WARNING missing required columns: {missing}")
    else:
        msgs.append("required columns present")
    return msgs
