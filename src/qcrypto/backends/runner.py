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
    backend_name: str | None = None,
) -> dict[str, int]:
    """Execute ``circuit`` and return measurement counts.

    Args:
        circuit: A measured circuit.
        shots: Number of repetitions.
        backend: ``"aer"`` for the local simulator, ``"ibm"`` for IBM Quantum
            hardware (requires the hardware extra and saved credentials).
        seed: Optional simulator seed for reproducible demonstrations (Aer only).
        optimization_level: Transpiler optimization level.
        backend_name: For ``"ibm"``, a specific device name; ``None`` picks the
            least-busy operational device.

    Returns:
        Mapping from measured bitstring to frequency.
    """
    if backend == "aer":
        return _run_aer(circuit, shots=shots, seed=seed, optimization_level=optimization_level)
    if backend == "ibm":
        from qcrypto.backends.ibm import run_ibm

        return run_ibm(
            circuit,
            shots=shots,
            backend_name=backend_name,
            optimization_level=max(optimization_level, 3),
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
