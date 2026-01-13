# Beginner Quick Start

This guide is intended for **non-technical users** and reviewers exploring this project as part of a public GitHub portfolio.

## What this project is
This repository demonstrates a **privacy-first sports science data pipeline** that mirrors how
professional and collegiate teams safely handle athlete performance data.

All examples use **synthetic data only**.

## First-time setup
From the project root:

```bash
python scripts/first_time_setup.py
```

This installs all dependencies in a local virtual environment.

## Running the application
```bash
python -m gui.main_window
```

A graphical interface will open. If a local `.venv` exists, the GUI will auto-reexec into it.

## Typical demo workflow
1. Place demo CSV files into `data/raw/`
2. Click **Process Raw Data**
3. Click **Run ML Project**
4. Click **Re-identify for Upload** (dry-run demo)

## Important notes
- No real athlete data is included
- Identity keys are local-only and empty by default
- Upload actions run in safe dry-run mode
- **Advanced Mode** reveals export and Git tools; it is optional for beginners
- Anonymization defaults live in `config/config.yaml`

If anything fails, see `docs/TROUBLESHOOTING.md`.
