"""qcrypto — a hands-on, honest tour of quantum computing's impact on cryptography.

The package is organised by *concept*, not by algorithm dumping ground:

* ``qcrypto.classical`` — purely classical building blocks (number theory, RSA,
  classical factoring). This is the Phase 0 foundation and has no quantum deps.
* ``qcrypto.quantum``   — Shor / Grover implementations (added from Phase 1).
* ``qcrypto.cli``       — the staged Rich CLI used for guided demonstrations.

Design principle: every quantum result is compared against a classical baseline
so the reader can see *exactly* what quantum computing does and does not buy us.
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = ["__version__"]
