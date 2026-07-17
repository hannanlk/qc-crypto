"""Post-quantum cryptography (Phase 4): ML-KEM (FIPS 203).

We wrap the pure-Python ``kyber-py`` reference implementation for the actual
lattice cryptography and add the educational/inspection layer on top. To be
explicit about the trust boundary: the KEM math (key generation, encapsulation,
decapsulation) is ``kyber-py``'s; everything in this subpackage is presentation,
size accounting, and framing. Neither is side-channel hardened — this is for
learning, exactly like the rest of the project.
"""

from __future__ import annotations

from qcrypto.pqc.mlkem import (
    PARAMETER_SETS,
    KEMRoundTrip,
    MLKEMParameterSet,
    parameter_table,
    run_roundtrip,
)

__all__ = [
    "PARAMETER_SETS",
    "KEMRoundTrip",
    "MLKEMParameterSet",
    "parameter_table",
    "run_roundtrip",
]
