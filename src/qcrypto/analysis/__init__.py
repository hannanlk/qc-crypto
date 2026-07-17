"""Analysis helpers: honest, quantitative framing of quantum threats.

Currently: symmetric-cipher security under Grover (the "why AES survives" numbers).
These are pure-Python and Qiskit-free so they can back both the article's tables
and the CLI without a quantum backend.
"""

from __future__ import annotations

from qcrypto.analysis.symmetric_security import (
    CipherSecurity,
    grover_security_table,
)

__all__ = ["CipherSecurity", "grover_security_table"]
