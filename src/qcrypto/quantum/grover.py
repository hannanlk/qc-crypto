"""Grover's algorithm: quadratic speedup for unstructured search.

Grover is the counterpoint to Shor. Where Shor gives an *exponential* speedup for
the structured problem of factoring, Grover gives only a *quadratic* speedup for
unstructured search: finding a marked item among N takes ~√N queries instead of N.

That quadratic-vs-exponential distinction is the whole reason quantum computing
threatens RSA (asymmetric) far more than AES (symmetric). Attacking a k-bit
symmetric key is unstructured search over 2^k keys; Grover turns 2^k into 2^(k/2)
queries — it *halves the exponent*, it does not collapse it. See
:mod:`qcrypto.analysis.symmetric_security` for what that means in practice (spoiler:
double the key size and you are fine; AES-256 stays ~128-bit secure).

This module demonstrates genuine Grover search on a toy space (mark an item among
2^n), so the mechanism is visible. We do NOT run Grover against a real AES oracle —
that is astronomically infeasible, and pretending otherwise would be exactly the
kind of hype this project avoids.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from qcrypto._logging import get_logger

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

logger = get_logger("grover")

__all__ = [
    "GroverResult",
    "optimal_iterations",
    "build_oracle",
    "build_diffuser",
    "build_grover_circuit",
    "search",
]


@dataclass
class GroverResult:
    """Outcome of a Grover search."""

    n_qubits: int
    marked: list[int]
    iterations: int
    shots: int
    counts: dict[str, int] = field(default_factory=dict)
    top_state: int | None = None
    success_probability: float = 0.0

    @property
    def found(self) -> bool:
        return self.top_state in self.marked


def optimal_iterations(n_qubits: int, num_marked: int = 1) -> int:
    """Optimal Grover iteration count ≈ (π/4)·√(N/M).

    This is where the quadratic speedup is literally visible: the iteration count
    scales as √N, not N.
    """
    if num_marked < 1:
        raise ValueError("num_marked must be >= 1")
    n = 1 << n_qubits
    if num_marked >= n:
        return 0
    return max(1, round((math.pi / 4) * math.sqrt(n / num_marked)))


def _as_state_list(marked: int | Sequence[int], n_qubits: int) -> list[int]:
    states = [marked] if isinstance(marked, int) else list(marked)
    limit = 1 << n_qubits
    for s in states:
        if not 0 <= s < limit:
            raise ValueError(f"marked state {s} out of range for {n_qubits} qubits")
    return states


def _phase_flip_all_ones(qc: QuantumCircuit, qubits: list[int]) -> None:
    """Flip the phase of |11...1> via a multi-controlled Z."""
    *controls, target = qubits
    if not controls:
        qc.z(target)
        return
    qc.h(target)
    qc.mcx(controls, target)
    qc.h(target)


def build_oracle(n_qubits: int, marked: int | Sequence[int]) -> QuantumCircuit:
    """Phase oracle that flips the sign of each marked computational basis state."""
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(n_qubits, name="oracle")
    for state in _as_state_list(marked, n_qubits):
        zeros = [i for i in range(n_qubits) if not (state >> i) & 1]
        for i in zeros:
            qc.x(i)
        _phase_flip_all_ones(qc, list(range(n_qubits)))
        for i in zeros:
            qc.x(i)
    return qc


def build_diffuser(n_qubits: int) -> QuantumCircuit:
    """The Grover diffusion operator (inversion about the mean)."""
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(n_qubits, name="diffuser")
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    _phase_flip_all_ones(qc, list(range(n_qubits)))
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    return qc


def build_grover_circuit(
    n_qubits: int, marked: int | Sequence[int], iterations: int | None = None
) -> QuantumCircuit:
    """Assemble a full Grover circuit: superposition, then oracle+diffuser rounds."""
    from qiskit import QuantumCircuit

    states = _as_state_list(marked, n_qubits)
    if iterations is None:
        iterations = optimal_iterations(n_qubits, len(states))

    qc = QuantumCircuit(n_qubits, n_qubits)
    qc.h(range(n_qubits))
    oracle = build_oracle(n_qubits, states).to_gate()
    diffuser = build_diffuser(n_qubits).to_gate()
    for _ in range(iterations):
        qc.append(oracle, range(n_qubits))
        qc.append(diffuser, range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def search(
    n_qubits: int,
    marked: int | Sequence[int],
    *,
    iterations: int | None = None,
    shots: int = 2048,
    backend: str = "aer",
    seed: int | None = None,
) -> GroverResult:
    """Run Grover search and report the top outcome and success probability."""
    states = _as_state_list(marked, n_qubits)
    iters = optimal_iterations(n_qubits, len(states)) if iterations is None else iterations
    circuit = build_grover_circuit(n_qubits, states, iters)

    from qcrypto.backends import run_counts

    counts = run_counts(circuit, shots=shots, backend=backend, seed=seed)
    total = sum(counts.values()) or 1
    marked_shots = sum(c for b, c in counts.items() if int(b.replace(" ", ""), 2) in states)
    top = max(counts, key=lambda b: counts[b])

    result = GroverResult(
        n_qubits=n_qubits,
        marked=states,
        iterations=iters,
        shots=shots,
        counts=counts,
        top_state=int(top.replace(" ", ""), 2),
        success_probability=marked_shots / total,
    )
    logger.info(
        "Grover: %d qubits, %d iters -> top=%s, P(success)=%.3f",
        n_qubits,
        iters,
        result.top_state,
        result.success_probability,
    )
    return result
