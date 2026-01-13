"""Vendor schema adapters (Catapult, VALD ForceDecks, etc.)."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple
import pandas as pd

@dataclass(frozen=True)
class AdapterResult:
    df: pd.DataFrame
    warnings: Tuple[str, ...] = ()

def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df

def detect_vendor(files: Iterable[Path]) -> str:
    files = list(files)
    names = " ".join([f.name.lower() for f in files])
    if "catapult" in names or "openfield" in names:
        return "catapult"
    if "forcedecks" in names or "vald" in names:
        return "vald_forcedecks"
    return "other"

def _pick(df: pd.DataFrame, candidates: tuple[str, ...]):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def load_catapult_csv(path: Path) -> AdapterResult:
    df = _standardize_columns(pd.read_csv(path))
    warnings = []
    athlete_col = _pick(df, ("athlete_id","player_id","external_id","id"))
    name_col = _pick(df, ("athlete_name","player_name","name"))
    dt_col = _pick(df, ("datetime_utc","start_time","date_time","datetime","timestamp","session_start"))
    sess_col = _pick(df, ("session_id","activity_id","session","id_session"))

    if athlete_col is None:
        df["athlete_id"] = pd.NA
        warnings.append("Catapult adapter: athlete_id missing; anonymize will derive if possible.")
    else:
        df.rename(columns={athlete_col:"athlete_id"}, inplace=True)

    if name_col and name_col != "athlete_name":
        df.rename(columns={name_col:"athlete_name"}, inplace=True)

    if dt_col is None:
        df["datetime_utc"] = pd.NA
        warnings.append("Catapult adapter: datetime missing; set to NA.")
    else:
        df.rename(columns={dt_col:"datetime_utc"}, inplace=True)

    if sess_col is None:
        df["session_id"] = pd.NA
    else:
        df.rename(columns={sess_col:"session_id"}, inplace=True)

    df["vendor"] = "catapult"
    return AdapterResult(df, tuple(warnings))

def load_vald_forcedecks_csv(path: Path) -> AdapterResult:
    df = _standardize_columns(pd.read_csv(path))
    warnings = []
    athlete_col = _pick(df, ("athlete_id","participant_id","id_athlete"))
    name_col = _pick(df, ("athlete_name","athlete","name","participant"))
    dt_col = _pick(df, ("datetime_utc","date","test_date","datetime","timestamp"))
    sess_col = _pick(df, ("session_id","session","test","trial","id"))

    if athlete_col is None:
        df["athlete_id"] = pd.NA
        warnings.append("ForceDecks adapter: athlete_id missing; anonymize will derive from name if present.")
    else:
        df.rename(columns={athlete_col:"athlete_id"}, inplace=True)

    if name_col and name_col != "athlete_name":
        df.rename(columns={name_col:"athlete_name"}, inplace=True)

    if dt_col is None:
        df["datetime_utc"] = pd.NA
    else:
        df.rename(columns={dt_col:"datetime_utc"}, inplace=True)

    if sess_col is None:
        df["session_id"] = pd.NA
    else:
        df.rename(columns={sess_col:"session_id"}, inplace=True)

    df["vendor"] = "vald_forcedecks"
    return AdapterResult(df, tuple(warnings))
