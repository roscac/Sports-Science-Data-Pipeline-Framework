"""Simple logging utilities with username in every record."""
from __future__ import annotations
import logging
from pathlib import Path
from datetime import datetime, timezone
import getpass

def get_logger(project_root: Path, name: str) -> logging.Logger:
    """Create a logger that writes to logs/ and stdout."""
    logs = project_root / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    user = getpass.getuser()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    log_path = logs / f"{name}_{ts}.log"

    logger = logging.getLogger(f"{name}_{user}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter(f"[%(asctime)s] USER:{user} %(levelname)s %(message)s")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger
