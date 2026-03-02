"""Observability primitives for the application."""

from __future__ import annotations

import logging
import os


def configure_logging() -> None:
    """Configure root logging once for the app."""
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
