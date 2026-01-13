# Sports Science Data Pipeline Framework
**A privacy-first, end-to-end framework for athlete performance data**

This repository provides a **production-inspired framework** for handling athlete performance data in
**pro and collegiate sports environments**, with a strong emphasis on **privacy, governance, and usability**.

It demonstrates how real teams can safely:
- process vendor exports (GPS, force plates, etc.)
- run machine learning on anonymized data
- securely re-identify outputs for reporting
- support non-technical users through a GUI
- provide advanced tools (Git + export) for technical reviewers
- maintain auditability and data governance

> ⚠️ **This is a public demonstration framework.**
> All examples use synthetic data and stubs. It is not intended for live athlete deployment without
> organizational review and approval.

---

## Why This Matters

Athlete data is sensitive, regulated, and increasingly complex.

Most public analytics projects focus only on models or dashboards.
In real team environments, the harder problems are:
- preventing accidental identity exposure
- supporting staff with mixed technical skill levels
- ensuring ML models never see athlete names
- enabling secure reporting back into athlete management systems
- making projects reproducible and shareable without leaking data

This framework addresses those problems directly.

It is designed to reflect **how high-performance teams actually work**, not toy examples.

---

## What This Project Demonstrates

- Privacy-first system design
- Athlete anonymization & controlled re-identification
- End-to-end ML workflow integration
- GUI-driven workflows for non-technical users
- Secure export and sharing patterns
- Audit logging and operational safeguards

---

## High-Level Data Flow

```
Vendor Exports
   ↓
Raw Data (local only)
   ↓
Anonymized ML Inputs
   ↓
ML Model Outputs
   ↓
Secure Re-identification (local only)
   ↓
Reporting / Upload
```

---

## Project Structure (Simplified)

```
data/
  raw/            # vendor exports (local only)
  ml_input/       # anonymized ML inputs
  upload/         # re-identified outputs (local only)

ml_models/
  load_dose/
    outputs/      # ML outputs (upload source)

gui/              # user-facing application
scripts/          # processing, ML, security logic
docs/             # SOPs, privacy, troubleshooting
config/           # project configuration (anonymization defaults)
```

---

## Getting Started (Demo)

```bash
pip install cookiecutter
cookiecutter .
python scripts/first_time_setup.py
python -m gui.main_window
```

The GUI auto-reexecs into `.venv` if it exists. You can also run `./launch_gui.sh`.

For a CLI-only anonymization pass:
```bash
python scripts/anonymize_raw.py
```

Sample synthetic data is available in `sample_data/` for quick demos.
Copy it into `data/raw/` and run the pipeline:
```bash
cp sample_data/demo_raw_sessions.csv data/raw/
```

---

## Documentation

- `docs/BEGINNER_QUICKSTART.md`
- `docs/ADVANCED_REFERENCE.md`
- `docs/PRIVACY_AND_SECURITY.md`
- `docs/TEAMWORKS_INGESTION.md`
- `docs/TROUBLESHOOTING.md`

---

## Intended Audience

- Sports scientists
- Performance analysts
- Sports technology engineers
- Data scientists in regulated environments
- Product and analytics roles in sports tech

---

## License

MIT License
