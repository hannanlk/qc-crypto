"""Tests for Grover search (require the quantum extra; auto-skipped otherwise)."""

from __future__ import annotations

import pytest

pytest.importorskip("qiskit")
pytest.importorskip("qiskit_aer")

from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import Statevector  # noqa: E402

from qcrypto.quantum.grover import (  # noqa: E402
    build_oracle,
    optimal_iterations,
    search,
)


def test_optimal_iterations() -> None:
    assert optimal_iterations(4, 1) == 3  # round(pi/4 * 4)
    assert optimal_iterations(3, 1) == 2
    assert optimal_iterations(2, 4) == 0  # everything marked -> nothing to search


def test_optimal_iterations_rejects_zero_marked() -> None:
    with pytest.raises(ValueError):
        optimal_iterations(4, 0)


def test_oracle_flips_only_marked_phase() -> None:
    n, marked = 3, 5
    qc = QuantumCircuit(n)
    qc.h(range(n))
    qc.append(build_oracle(n, marked).to_gate(), range(n))
    amplitudes = Statevector(qc).data
    assert amplitudes[marked].real < 0
    assert all(amplitudes[j].real > 0 for j in range(2**n) if j != marked)


def test_search_finds_single_marked_state() -> None:
    result = search(4, 9, shots=1024, seed=7)
    assert result.found
    assert result.top_state == 9
    assert result.success_probability > 0.9


def test_search_finds_one_of_two_marked_states() -> None:
    result = search(4, [3, 12], shots=1024, seed=7)
    assert result.top_state in (3, 12)
    assert result.success_probability > 0.8


def test_search_rejects_out_of_range_marked() -> None:
    with pytest.raises(ValueError):
        search(3, 99, shots=256)
