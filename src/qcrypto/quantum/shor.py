"""Shor's algorithm: factoring by quantum period-finding.

The reframing at the core of Shor is that *factoring reduces to order-finding*.
To factor ``N``:

1. Pick ``a`` coprime to ``N``.
2. Find the order ``r`` — the smallest ``r > 0`` with ``a^r ≡ 1 (mod N)``.
   This is the step that is classically hard and quantum-mechanically easy: the
   quantum circuit estimates a phase ``s/r`` via the inverse QFT.
3. If ``r`` is even and ``a^{r/2} != -1 (mod N)``, then ``gcd(a^{r/2} ± 1, N)``
   are non-trivial factors.

Steps 1 and 3 are classical (see :mod:`qcrypto.quantum.post_process`); only step 2
is quantum. This module assembles the order-finding circuit and orchestrates a run.

Scope: a faithful demonstration on toy moduli (default target: N = 21). The
modular-multiplier oracle is simulator-scale by construction — see
:mod:`qcrypto.quantum.modular_arithmetic` for the honesty discussion.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import gcd
from typing import TYPE_CHECKING

from qcrypto._logging import get_logger
from qcrypto.classical.number_theory import is_prime
from qcrypto.quantum.post_process import recover_factors_from_counts

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

logger = get_logger("shor")

__all__ = ["ShorResult", "default_counting_qubits", "build_order_finding_circuit", "factor"]


@dataclass
class ShorResult:
    """Outcome of a Shor factoring attempt."""

    modulus: int
    base: int
    n_count: int
    shots: int
    counts: dict[str, int] = field(default_factory=dict)
    order: int | None = None
    factors: tuple[int, int] | None = None
    lucky_base: bool = False
    num_qubits: int = 0
    circuit_depth: int = 0

    @property
    def success(self) -> bool:
        return self.factors is not None and self.factors[0] * self.factors[1] == self.modulus


def default_counting_qubits(modulus: int) -> int:
    """Counting-register width. 2·ceil(log2 N) guarantees enough phase resolution
    to recover the order via continued fractions (needs ``2^t >= N^2``)."""
    return 2 * modulus.bit_length()


def build_order_finding_circuit(base: int, modulus: int, n_count: int) -> QuantumCircuit:
    """Assemble the quantum order-finding circuit for ``base`` modulo ``modulus``.

    Structure: a counting register in uniform superposition controls the modular
    exponentiation ``|1> -> |base^x mod N>`` (via ``U_{base^{2^j}}`` on each qubit),
    then an inverse QFT concentrates amplitude at phases ``s/r``, which we measure.
    """
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    from qcrypto.quantum.modular_arithmetic import controlled_modular_multiplier
    from qcrypto.quantum.qft import build_qft

    n_work = modulus.bit_length()
    counting = QuantumRegister(n_count, "count")
    work = QuantumRegister(n_work, "work")
    measured = ClassicalRegister(n_count, "m")
    qc = QuantumCircuit(counting, work, measured)

    qc.h(counting[:])
    qc.x(work[0])  # initialise work register to |1>

    # Controlled U^(2^j): use (U_a)^(2^j) = U_{a^{2^j} mod N} so each counting
    # qubit drives a single modular multiplier by a precomputed constant.
    for j in range(n_count):
        constant = pow(base, 1 << j, modulus)
        gate = controlled_modular_multiplier(constant, modulus, n_work)
        qc.append(gate, [counting[j], *work[:]])

    qc.append(build_qft(n_count, inverse=True).to_gate(), counting[:])
    qc.measure(counting, measured)
    return qc


def factor(
    modulus: int,
    *,
    base: int | None = None,
    n_count: int | None = None,
    shots: int = 2048,
    backend: str = "aer",
    seed: int | None = None,
    backend_name: str | None = None,
) -> ShorResult:
    """Attempt to factor ``modulus`` with Shor's algorithm.

    Args:
        modulus: Odd composite to factor (default demonstration target: 21).
        base: Coprime base ``a``; defaults to 2 when valid, else the smallest
            valid base. If ``gcd(base, N) > 1`` we get a factor classically for
            free (the "lucky base" case) and skip the circuit.
        n_count: Counting-register width; defaults to :func:`default_counting_qubits`.
        shots, backend, seed: Execution parameters passed to the runner.

    Raises:
        ValueError: if ``modulus`` is even, prime, or < 3.
    """
    if modulus < 3 or modulus % 2 == 0:
        raise ValueError("modulus must be an odd integer >= 3")
    if is_prime(modulus):
        raise ValueError(f"{modulus} is prime; nothing to factor")

    base = _select_base(modulus) if base is None else base
    if not 1 < base < modulus:
        raise ValueError(f"base must satisfy 1 < base < N; got {base}")

    # Lucky base: an accidental common factor hands us the answer with no circuit.
    common = gcd(base, modulus)
    if common > 1:
        logger.info("Lucky base %d shares factor %d with N=%d", base, common, modulus)
        return ShorResult(
            modulus=modulus,
            base=base,
            n_count=0,
            shots=0,
            factors=(min(common, modulus // common), max(common, modulus // common)),
            lucky_base=True,
        )

    n_count = default_counting_qubits(modulus) if n_count is None else n_count
    circuit = build_order_finding_circuit(base, modulus, n_count)

    from qcrypto.backends import run_counts

    counts = run_counts(
        circuit, shots=shots, backend=backend, seed=seed, backend_name=backend_name
    )

    result = ShorResult(
        modulus=modulus,
        base=base,
        n_count=n_count,
        shots=shots,
        counts=counts,
        num_qubits=circuit.num_qubits,
        circuit_depth=circuit.depth(),
    )
    recovered = recover_factors_from_counts(counts, base, modulus, n_count)
    if recovered is not None:
        result.order, result.factors = recovered
        logger.info("Recovered order r=%d -> factors %s", result.order, result.factors)
    else:
        logger.warning("No usable order recovered from %d shots; retry or change base", shots)
    return result


def _select_base(modulus: int) -> int:
    """Pick a base coprime to ``modulus``, preferring the canonical 2."""
    if gcd(2, modulus) == 1:
        return 2
    for candidate in range(3, modulus):
        if gcd(candidate, modulus) == 1:
            return candidate
    raise ValueError(f"no valid base found for N={modulus}")  # pragma: no cover
