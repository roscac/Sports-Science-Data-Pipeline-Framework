# Advanced Reference

This document is for **technical reviewers, engineers, and sports scientists**.

## Architecture overview
- Raw data is isolated from analytics
- ML pipelines operate only on anonymized identifiers
- Re-identification is explicit, local, and auditable

## Key folders
- `data/raw/`: vendor exports (local-only)
- `data/ml_input/`: anonymized ML inputs
- `ml_models/<project>/outputs/`: model outputs
- `data/upload/`: re-identified outputs (local-only)

## ML integration
Replace logic in:
```text
scripts/ml_integration.py
```

All model outputs must be written to:
```text
ml_models/<project_name>/outputs/
```

## Git usage
- Sensitive folders are blocked via `.gitignore`
- GUI exposes Git controls and Export Project in Advanced Mode
- Advanced Mode includes an optional auto-delete toggle for ML outputs after re-identify
- Standard CLI Git usage is fully supported

## Anonymization configuration
Defaults live in `config/config.yaml`:
- `identifier_column`: source ID column used for pseudonyms
- `name_column`: fallback name column if IDs are missing
- `pii_columns`: columns to drop after anonymization
- `hmac_key_path`: local-only key used for HMAC pseudonyms
- `identity_key_path`: local-only lookup key for re-identification

For a CLI-only run:
```text
python scripts/anonymize_raw.py
```

## Testing
```bash
pytest -q
```

Tests focus on privacy and export safety.
