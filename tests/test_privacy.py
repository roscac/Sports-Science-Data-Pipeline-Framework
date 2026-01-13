from pathlib import Path
import pandas as pd
import tempfile

from scripts.anonymize import anonymize_dataframe
from scripts.export_project import export_project

def test_anonymize_drops_names():
    df = pd.DataFrame({
        "athlete_id": ["123", "456"],
        "athlete_name": ["Alice", "Bob"],
        "datetime_utc": ["2025-01-01T00:00:00Z", "2025-01-01T01:00:00Z"],
        "session_id": ["s1", "s1"],
    })
    with tempfile.TemporaryDirectory() as td:
        pr = Path(td)
        out = anonymize_dataframe(df, pr)
        assert "athlete_name" not in out.df.columns
        assert "athlete_id" in out.df.columns

def test_export_skips_sensitive_folders():
    with tempfile.TemporaryDirectory() as td:
        pr = Path(td) / "proj"
        pr.mkdir()
        (pr / "data/raw").mkdir(parents=True)
        (pr / "data/identity_key").mkdir(parents=True)
        (pr / "data/upload").mkdir(parents=True)
        (pr / "logs").mkdir(parents=True)
        (pr / "config").mkdir(parents=True)

        (pr / "data/raw/raw.csv").write_text("secret")
        (pr / "data/identity_key/identity_key.csv").write_text("supersecret")
        (pr / "data/upload/upload.csv").write_text("names")
        (pr / "config/config.yaml").write_text("ok")

        dest = Path(td) / "exported"
        export_project(pr, dest)

        assert not (dest / "data/raw/raw.csv").exists()
        assert not (dest / "data/identity_key/identity_key.csv").exists()
        assert not (dest / "data/upload/upload.csv").exists()
        assert (dest / "config/config.yaml").exists()
