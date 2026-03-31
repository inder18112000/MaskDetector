"""
Centralised logging for the MaskDetector application.

Usage anywhere in the project:
    from app.logger import get
    _log = get(__name__)
    _log.info("started")
    _log.exception("DB error during migration")

Log levels:
  DEBUG   — verbose tracing (written to file only)
  INFO    — normal operational events
  WARNING — recoverable problems (written to file + stderr)
  ERROR / CRITICAL — serious failures
"""

import logging
import sys
from pathlib import Path

_LOG_FILE = Path(__file__).parent.parent / "maskdetector.log"

_FMT = "%(asctime)s %(levelname)-8s %(name)s — %(message)s"
_DATE = "%Y-%m-%d %H:%M:%S"


def _configure() -> None:
    root = logging.getLogger()
    if root.handlers:
        return  # Already configured (e.g. during tests)

    root.setLevel(logging.DEBUG)

    # File handler — captures everything (DEBUG+)
    try:
        fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(_FMT, datefmt=_DATE))
        root.addHandler(fh)
    except OSError:
        pass  # Non-writable location; skip file logging

    # Console handler — warnings and above only
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.WARNING)
    ch.setFormatter(logging.Formatter(_FMT, datefmt=_DATE))
    root.addHandler(ch)


_configure()


def get(name: str) -> logging.Logger:
    """Return a named logger.  Call once per module: _log = get(__name__)"""
    return logging.getLogger(name)
