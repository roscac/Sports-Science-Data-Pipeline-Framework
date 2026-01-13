"""Configurable anonymization helpers using HMAC pseudonyms."""
from __future__ import annotations
import hashlib
import hmac
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import pandas as pd
import yaml

DEFAULT_IDENTIFIER_COLUMN = "athlete_id"
DEFAULT_NAME_COLUMN = "athlete_name"
DEFAULT_PII_COLUMNS = ("athlete_name",)
DEFAULT_KEY_PATH = "data/identity_key/hmac_key.txt"
DEFAULT_IDENTITY_KEY_PATH = "data/identity_key/identity_key.csv"
DEFAULT_PSEUDONYM_COLUMN = "athlete_id"


@dataclass(frozen=True)
class AnonymizationSettings:
    identifier_column: str
    name_column: str
    pii_columns: Tuple[str, ...]
    hmac_key_path: str
    identity_key_path: str
    pseudonym_column: str


def load_config(project_root: Path) -> Dict[str, Any]:
    """Load config.yaml into a dict, or return empty config."""
    config_path = project_root / "config" / "config.yaml"
    if not config_path.exists():
        return {}
    data = yaml.safe_load(config_path.read_text()) or {}
    return data if isinstance(data, dict) else {}


def load_settings(project_root: Path) -> AnonymizationSettings:
    """Resolve anonymization settings with defaults."""
    config = load_config(project_root)
    anon = config.get("anonymization", {}) if isinstance(config, dict) else {}
    pii_cols = anon.get("pii_columns", DEFAULT_PII_COLUMNS)
    if isinstance(pii_cols, str):
        pii_cols = [pii_cols]
    return AnonymizationSettings(
        identifier_column=anon.get("identifier_column", DEFAULT_IDENTIFIER_COLUMN),
        name_column=anon.get("name_column", DEFAULT_NAME_COLUMN),
        pii_columns=tuple(str(c) for c in pii_cols),
        hmac_key_path=anon.get("hmac_key_path", DEFAULT_KEY_PATH),
        identity_key_path=anon.get("identity_key_path", DEFAULT_IDENTITY_KEY_PATH),
        pseudonym_column=anon.get("pseudonym_column", DEFAULT_PSEUDONYM_COLUMN),
    )


def load_or_create_key(project_root: Path, key_path: str) -> bytes:
    """Load or create a local HMAC key (never committed)."""
    key_file = project_root / key_path
    key_file.parent.mkdir(parents=True, exist_ok=True)
    if key_file.exists():
        key_text = key_file.read_text().strip()
        return bytes.fromhex(key_text)
    key = secrets.token_bytes(32)
    key_file.write_text(key.hex())
    return key


def hmac_anon_id(value: str, key: bytes) -> str:
    """Create a stable pseudonym for a value using HMAC."""
    digest = hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest[:16]


def _pick_source_column(df: pd.DataFrame, settings: AnonymizationSettings) -> Tuple[str | None, Tuple[str, ...]]:
    """Select the best source column to pseudonymize and warnings."""
    warnings: Iterable[str] = []
    if settings.identifier_column in df.columns and df[settings.identifier_column].notna().any():
        return settings.identifier_column, ()
    if settings.name_column in df.columns and df[settings.name_column].notna().any():
        return settings.name_column, (f"Anonymize: using {settings.name_column} because {settings.identifier_column} missing.",)
    return None, (f"Anonymize: no {settings.identifier_column} or {settings.name_column} found; IDs set to NA.",)


def apply_anonymization(df: pd.DataFrame, project_root: Path) -> Tuple[pd.DataFrame, pd.DataFrame, Tuple[str, ...]]:
    """Apply pseudonymization and drop configured PII columns."""
    df = df.copy()
    settings = load_settings(project_root)
    warnings: list[str] = []

    src, src_warnings = _pick_source_column(df, settings)
    warnings.extend(src_warnings)

    if src is None:
        df[settings.pseudonym_column] = pd.NA
        key_df = pd.DataFrame(columns=["anon_id", settings.name_column])
        drop_cols = [c for c in settings.pii_columns if c in df.columns]
        if drop_cols:
            df = df.drop(columns=drop_cols, errors="ignore")
        return df, key_df, tuple(warnings)

    key = load_or_create_key(project_root, settings.hmac_key_path)
    anon_ids = df[src].astype(str).map(lambda v: hmac_anon_id(v, key) if v and v != "nan" else pd.NA)
    df[settings.pseudonym_column] = anon_ids

    key_columns = {"anon_id": anon_ids, src: df[src]}
    if settings.name_column in df.columns and settings.name_column not in key_columns:
        key_columns[settings.name_column] = df[settings.name_column]
    key_df = pd.DataFrame(key_columns).dropna().drop_duplicates(subset=["anon_id"])

    drop_cols = [c for c in settings.pii_columns if c in df.columns]
    if drop_cols:
        df = df.drop(columns=drop_cols, errors="ignore")
    if src != settings.pseudonym_column and src in df.columns:
        df = df.drop(columns=[src], errors="ignore")
    return df, key_df, tuple(warnings)
