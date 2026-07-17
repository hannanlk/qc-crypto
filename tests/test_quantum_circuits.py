"""Tests for the quantum building blocks and end-to-end Shor factoring.

These require the optional quantum extra (``pip install -e ".[quantum]"``) and are
skipped automatically when Qiskit / Aer are absent, so the classical CI stays fast.
"""

from __future__ import annotations

import pytest

pytest.importorskip("qiskit")
pytest.importorskip("qiskit_aer")

import numpy as np  # noqa: E402
from qiskit.quantum_info import Operator  # noqa: E402

from qcrypto.quantum import shor  # noqa: E402
from qcrypto.quantum.modular_arithmetic import (  # noqa: E402
    classical_modular_multiply,
    permutation_matrix,
)
from qcrypto.quantum.qft import build_qft  # noqa: E402


def _dft_matrix(n: int) -> np.ndarray:
    """The standard QFT (with bit-reversal) unitary: F[j,k] = w^{jk}/sqrt(N)."""
    dim = 2**n
    omega = np.exp(2j * np.pi / dim)
    j, k = np.meshgrid(np.arange(dim), np.arange(dim), indexing="ij")
    return omega ** (j * k) / np.sqrt(dim)


@pytest.mark.parametrize("n", [3, 4])
def test_custom_qft_matches_dft(n: int) -> None:
    """Our hand-built QFT must equal the mathematical DFT (up to global phase).

    We accept either qubit endianness: a correct QFT equals the DFT under one of
    the two qubit orderings (Qiskit is little-endian; our textbook construction
    treats qubit 0 as most-significant). ``reverse_qargs`` flips that ordering.
    Comparing against a plain NumPy DFT keeps this independent of Qiskit's
    circuit-library version churn.
    """
    ours = Operator(build_qft(n))
    dft = Operator(_dft_matrix(n))
    assert ours.equiv(dft) or ours.equiv(dft.reverse_qargs())


@pytest.mark.parametrize("n", [3, 4])
def test_inverse_qft_undoes_qft(n: int) -> None:
    forward = Operator(build_qft(n))
    inverse = Operator(build_qft(n, inverse=True))
    assert forward.compose(inverse).equiv(Operator(np.eye(2**n)))


def test_permutation_matrix_matches_classical_map() -> None:
    n_qubits = 5
    matrix = permutation_matrix(2, 21, n_qubits)
    for y in range(2**n_qubits):
        target = int(np.argmax(matrix[:, y]))
        assert target == classical_modular_multiply(2, y, 21)
        assert np.isclose(matrix[target, y], 1.0)


def test_permutation_matrix_is_unitary() -> None:
    matrix = permutation_matrix(2, 21, 5)
    assert np.allclose(matrix.conj().T @ matrix, np.eye(matrix.shape[0]))


def test_permutation_matrix_requires_coprime_base() -> None:
    with pytest.raises(ValueError):
        permutation_matrix(3, 21, 5)  # gcd(3, 21) = 3


def test_shor_rejects_prime() -> None:
    with pytest.raises(ValueError):
        shor.factor(23)


def test_shor_lucky_base_shortcut() -> None:
    result = shor.factor(21, base=3)  # gcd(3, 21) = 3, no circuit needed
    assert result.lucky_base
    assert result.factors is not None
    assert set(result.factors) == {3, 7}


@pytest.mark.slow
def test_shor_factors_21_on_simulator() -> None:
    result = shor.factor(21, base=2, n_count=8, shots=512, seed=1234)
    assert result.success
    assert result.order == 6
    assert result.factors is not None
    assert set(result.factors) == {3, 7}
