"""Run a circuit and return measurement counts.

Kept intentionally minimal and backend-agnostic at the call site: callers pass a
circuit and a backend name and get back a ``{bitstring: frequency}`` dict. Qiskit
is imported lazily so importing this module never requires the quantum extra.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qcrypto._logging import get_logger

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

logger = get_logger("backends")

__all__ = ["run_counts"]


def run_counts(
    circuit: QuantumCircuit,
    *,
    shots: int = 2048,
    backend: str = "aer",
    seed: int | None = None,
    optimization_level: int = 1,
) -> dict[str, int]:
    """Execute ``circuit`` and return measurement counts.

    Args:
        circuit: A measured circuit.
        shots: Number of repetitions.
        backend: ``"aer"`` for the local simulator. ``"ibm"`` is reserved for
            Phase 2 and currently raises with a pointer to the setup it needs.
        seed: Optional simulator seed for reproducible demonstrations.
        optimization_level: Transpiler optimization level.

    Returns:
        Mapping from measured bitstring to frequency.
    """
    if backend == "aer":
        return _run_aer(circuit, shots=shots, seed=seed, optimization_level=optimization_level)
    if backend == "ibm":
        raise NotImplementedError(
            "The IBM Quantum runtime backend is a Phase 2 deliverable and requires "
            "account credentials. Use backend='aer' for Phase 1."
        )
    raise ValueError(f"unknown backend {backend!r}")


def _run_aer(
    circuit: QuantumCircuit,
    *,
    shots: int,
    seed: int | None,
    optimization_level: int,
) -> dict[str, int]:
    from qiskit import transpile
    from qiskit_aer import AerSimulator

    simulator = AerSimulator(seed_simulator=seed)
    transpiled = transpile(circuit, simulator, optimization_level=optimization_level)
    logger.debug("Running on Aer: %d shots, depth=%d", shots, transpiled.depth())
    result = simulator.run(transpiled, shots=shots).result()
    counts: dict[str, int] = result.get_counts()
    return counts
