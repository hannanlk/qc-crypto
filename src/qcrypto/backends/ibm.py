"""IBM Quantum runtime backend (Phase 2).

Runs a circuit on real IBM Quantum hardware via ``qiskit-ibm-runtime``'s SamplerV2
primitive. This path is intentionally isolated from the Aer path so the rest of the
codebase (shor.py, the CLI) is backend-agnostic: the same order-finding circuit runs
on a simulator or on hardware by flipping one argument.

Prerequisites (see docs/ibm-quantum-setup.md):
  * an IBM Quantum account and API token,
  * credentials saved once via ``QiskitRuntimeService.save_account(...)``,
  * the hardware extra installed: ``pip install -e ".[hardware]"``.

IMPORTANT (honesty, again): running our genuine, un-simplified order-finding circuit
for N=21 on today's noisy hardware will not cleanly recover the period. Gate errors and
decoherence over the circuit's depth wash out the interference peaks. That failure is
not a bug — it is the entire point of Part 2: it is the concrete, measured gap between
the simulator's tidy result and what noisy intermediate-scale quantum (NISQ) devices can
actually do. Expect a broad, noisy histogram, and compare it honestly to the simulator.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qcrypto._logging import get_logger

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

logger = get_logger("backends.ibm")

__all__ = ["run_ibm"]


def run_ibm(
    circuit: QuantumCircuit,
    *,
    shots: int = 2048,
    backend_name: str | None = None,
    optimization_level: int = 3,
) -> dict[str, int]:
    """Transpile and run ``circuit`` on IBM Quantum hardware; return counts.

    Args:
        circuit: A measured circuit.
        shots: Number of shots.
        backend_name: Specific device (e.g. ``"ibm_kingston"``). If ``None``, the
            least-busy operational non-simulator backend is chosen.
        optimization_level: Transpiler effort (3 = maximum; important on hardware).

    Returns:
        Mapping from measured bitstring to frequency.

    Raises:
        RuntimeError: if credentials are missing or no backend is available. The
            message points at the setup guide rather than leaking a raw stack trace.
    """
    try:
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    except ImportError as exc:  # pragma: no cover - optional extra
        raise RuntimeError(
            'The IBM hardware backend needs the hardware extra: pip install -e ".[hardware]"'
        ) from exc

    try:
        service = QiskitRuntimeService()
    except Exception as exc:  # noqa: BLE001 - surface a friendly, actionable message
        raise RuntimeError(
            "Could not load IBM Quantum credentials. Save them once with "
            "QiskitRuntimeService.save_account(channel='ibm_quantum_platform', token=...). "
            "See docs/ibm-quantum-setup.md."
        ) from exc

    backend = (
        service.backend(backend_name)
        if backend_name
        else service.least_busy(operational=True, simulator=False)
    )
    logger.info("Running on IBM backend %s (%d qubits)", backend.name, backend.num_qubits)

    pass_manager = generate_preset_pass_manager(optimization_level=optimization_level, backend=backend)
    isa_circuit = pass_manager.run(circuit)

    sampler = SamplerV2(mode=backend)
    job = sampler.run([isa_circuit], shots=shots)
    logger.info("Submitted job %s; waiting for results (this may queue).", job.job_id())
    pub_result = job.result()[0]
    return _extract_counts(pub_result)


def _extract_counts(pub_result: Any) -> dict[str, int]:
    """Pull a counts dict out of a SamplerV2 pub result, register-name-agnostically.

    SamplerV2 returns measured bits in a ``DataBin`` keyed by classical-register name
    (our circuits use "m" for Shor, the default for Grover). We locate the single
    ``BitArray`` without hardcoding the register name.
    """
    data = pub_result.data
    # Preferred: DataBin's mapping interface (recent qiskit).
    try:
        for name in data.keys():  # type: ignore[attr-defined]
            return dict(data[name].get_counts())
    except AttributeError:
        pass
    # Fallback: find the first attribute exposing get_counts().
    for name in dir(data):
        if name.startswith("_"):
            continue
        value = getattr(data, name)
        if hasattr(value, "get_counts"):
            return dict(value.get_counts())
    raise RuntimeError("could not extract counts from the SamplerV2 result")
