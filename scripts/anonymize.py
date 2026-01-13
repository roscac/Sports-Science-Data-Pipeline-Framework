"""Convenience wrapper for anonymization helpers."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import pandas as pd

from scripts.helpers.anonymization import apply_anonymization, load_settings

@dataclass(frozen=True)
class AnonymizeResult:
    df: pd.DataFrame
    key_df: pd.DataFrame
    warnings: Tuple[str, ...] = ()

def anonymize_dataframe(df: pd.DataFrame, project_root: Path) -> AnonymizeResult:
    """Return anonymized DataFrame and identity-key rows for local storage."""
    anon_df, key_df, warnings = apply_anonymization(df, project_root)
    return AnonymizeResult(df=anon_df, key_df=key_df, warnings=tuple(warnings))

def write_identity_key(key_df: pd.DataFrame, project_root: Path) -> Path:
    """Merge identity-key rows into the local identity key file."""
    settings = load_settings(project_root)
    key_path = project_root / settings.identity_key_path
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if key_path.exists():
        existing = pd.read_csv(key_path)
        merged = pd.concat([existing, key_df], ignore_index=True).drop_duplicates(subset=["anon_id"])
    else:
        merged = key_df.drop_duplicates(subset=["anon_id"])
    merged.to_csv(key_path, index=False)
    return key_path
