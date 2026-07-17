"""Quantum implementations (Phase 1+): Shor's algorithm and its components.

Import policy: this package intentionally does **not** import Qiskit at package
import time. Qiskit is an optional dependency (``pip install -e ".[quantum]"``),
and we want ``import qcrypto`` and the classical CLI to work without it. Submodules
import Qiskit lazily inside functions, so ``from qcrypto.quantum import shor`` only
pulls Qiskit in when you actually build or run a circuit.
"""

from __future__ import annotations

__all__ = ["qft", "modular_arithmetic", "shor", "post_process"]
