"""Execution backends.

A thin seam between circuit construction and *where* a circuit runs. Phase 1 only
needs the Aer simulator, but isolating execution here means Phase 2 can add an IBM
Quantum runtime backend without touching any call site in ``shor.py`` or the CLI.
"""

from __future__ import annotations

from qcrypto.backends.runner import run_counts

__all__ = ["run_counts"]
