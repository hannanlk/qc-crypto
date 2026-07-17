"""Controlled modular multiplication — the oracle inside Shor's algorithm.

Shor's period-finding needs a controlled operation ``U_a : |y> -> |a·y mod N>``,
applied as ``U_a^(2^j)`` for each counting qubit ``j``. We exploit the identity
``(U_a)^(2^j) = U_{a^{2^j} mod N}``: rather than repeat a multiplier 2^j times,
we compute the classical constant ``a^{2^j} mod N`` and build *one* multiplier for
it. This is standard and keeps circuit depth manageable on a simulator.

Honesty note (this is central to the project's thesis):
    We construct ``U_a`` as an explicit permutation of basis states and hand it
    to Qiskit as a unitary. This is a *genuine* reversible modular multiplier —
    it computes the period, it does not hardcode the answer's period the way the
    infamous "compiled" Shor demonstrations do. But it is not the *deepest* form
    of honesty: a fully gate-level implementation (e.g. Beauregard's QFT adders)
    builds the same map from Toffoli/adder primitives without ever materialising
    the permutation classically. We flag exactly where on that spectrum we sit,
    and revisit the trade-off (depth vs. transparency) in the article.

Because we build a permutation matrix of size ``2^num_qubits``, this approach is
simulator-scale only. That is fine: the whole point of Phase 1 is a faithful,
inspectable demonstration on a toy modulus, not a scalable factoring engine.
"""

from __future__ import annotations

from math import gcd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from qiskit.circuit import Gate

__all__ = [
    "classical_modular_multiply",
    "permutation_matrix",
    "modular_multiplier_gate",
    "controlled_modular_multiplier",
]


def classical_modular_multiply(a: int, y: int, modulus: int) -> int:
    """Reference map used by :func:`permutation_matrix` and by tests.

    Values ``y >= modulus`` (unused by the algorithm but present in the register)
    are left fixed so the overall map is a bijection on all ``2^num_qubits`` states.
    """
    return (a * y) % modulus if y < modulus else y


def permutation_matrix(a: int, modulus: int, num_qubits: int) -> np.ndarray:
    """Build the permutation-unitary for ``|y> -> |a·y mod N>`` as a NumPy array."""
    import numpy as np

    if gcd(a, modulus) != 1:
        raise ValueError(f"a={a} must be coprime to N={modulus} for an invertible map")
    dim = 1 << num_qubits
    if modulus > dim:
        raise ValueError(f"register of {num_qubits} qubits too small for N={modulus}")

    matrix = np.zeros((dim, dim), dtype=complex)
    for y in range(dim):
        matrix[classical_modular_multiply(a, y, modulus), y] = 1.0
    return matrix


def modular_multiplier_gate(
    a: int, modulus: int, num_qubits: int, label: str | None = None
) -> Gate:
    """A single (uncontrolled) modular-multiplier gate for constant ``a``."""
    from qiskit.circuit.library import UnitaryGate

    matrix = permutation_matrix(a, modulus, num_qubits)
    return UnitaryGate(matrix, label=label or f"×{a} mod {modulus}")


def controlled_modular_multiplier(
    a: int, modulus: int, num_qubits: int, label: str | None = None
) -> Gate:
    """The controlled version appended once per counting qubit in Shor's circuit."""
    return modular_multiplier_gate(a, modulus, num_qubits, label).control(1)
