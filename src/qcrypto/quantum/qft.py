"""Quantum Fourier Transform — the heart of Shor's period-finding.

We hand-build the QFT (rather than only calling Qiskit's library version)
because *seeing* the Hadamard-plus-controlled-phase ladder is the point: it is
what turns a superposition with hidden period ``r`` into a distribution that
peaks at multiples of ``2^t / r``. The accompanying test asserts our circuit's
unitary equals Qiskit's ``QFT`` (up to global phase), so the educational version
is provably the real thing and safe to use in the Shor circuit.

Qubit/endianness note: with the final swap layer, the transform matches Qiskit's
default ``QFT(n, do_swaps=True)`` convention, so a measured bitstring can be read
as an ordinary big-endian... — see ``shor.py`` for exactly how the measured
integer is interpreted.
"""

from __future__ import annotations

from math import pi
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # import only for type checkers; avoids requiring Qiskit at import
    from qiskit import QuantumCircuit

__all__ = ["build_qft"]


def build_qft(num_qubits: int, *, inverse: bool = False, do_swaps: bool = True) -> QuantumCircuit:
    """Build a QFT (or inverse QFT) circuit on ``num_qubits`` qubits.

    Args:
        num_qubits: Register width.
        inverse: If True, return the inverse QFT (used to read out the phase).
        do_swaps: Append the bit-reversal swap layer (matches Qiskit's default).

    Returns:
        A named ``QuantumCircuit`` suitable for ``.to_gate()`` / ``compose``.
    """
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(num_qubits, name="QFT")
    for j in range(num_qubits):
        qc.h(j)
        for k in range(j + 1, num_qubits):
            # Controlled-phase is symmetric in its two qubits; the rotation angle
            # halves with distance, R_m with angle 2*pi/2^(k-j+1) = pi/2^(k-j).
            qc.cp(pi / (2 ** (k - j)), j, k)
    if do_swaps:
        for i in range(num_qubits // 2):
            qc.swap(i, num_qubits - 1 - i)

    if inverse:
        inv = qc.inverse()
        inv.name = "IQFT"
        return inv
    return qc
