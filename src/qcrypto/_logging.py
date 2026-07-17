"""Central logging configuration.

Why a dedicated module: we want library code to emit structured logs *without*
imposing a handler on importers (a library should never call ``basicConfig`` at
import time). Applications — the CLI, notebooks, tests — opt in by calling
:func:`configure_logging`. This keeps the library well-behaved when embedded in
someone else's project.
"""

from __future__ import annotations

import logging

from rich.logging import RichHandler

_CONFIGURED = False


def configure_logging(level: int = logging.INFO) -> None:
    """Attach a single Rich handler to the ``qcrypto`` logger tree.

    Idempotent: calling it more than once (e.g. from both the CLI and a test)
    will not stack duplicate handlers.

    Args:
        level: Standard :mod:`logging` level (e.g. ``logging.INFO``).
    """
    global _CONFIGURED
    if _CONFIGURED:
        logging.getLogger("qcrypto").setLevel(level)
        return

    handler = RichHandler(rich_tracebacks=True, show_path=False, markup=True)
    logger = logging.getLogger("qcrypto")
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the ``qcrypto`` namespace."""
    return logging.getLogger(f"qcrypto.{name}")
