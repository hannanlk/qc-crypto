# IBM Quantum Setup (Phase 2)

This guide gets you from zero to running Shor's circuit on a real IBM Quantum
device. Budget ~15 minutes for setup; actual hardware runs then queue.

## 1. Create an account

Sign up (free) at <https://quantum.cloud.ibm.com/>. The **Open Plan** is free and, as
of 2026, includes access to a Heron R2 processor (e.g. `ibm_kingston`, 156 qubits) with
roughly 180 minutes of QPU time per 12-month period. That is plenty for the small,
occasional runs in this project — but it is *metered*, so do not leave large jobs
looping.

## 2. Get your API token

From the dashboard, copy your **API token**. Treat it like a password — it must never
be committed. This repo's `.gitignore` already excludes `.env`, `*.token`, and the
`.qiskit/` credentials directory.

## 3. Install the hardware extra

```bash
python -m pip install -e ".[quantum,hardware]"
```

`[hardware]` adds `qiskit-ibm-runtime`.

## 4. Save your credentials once

In a Python shell:

```python
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",
    token="PASTE_YOUR_TOKEN_HERE",
    overwrite=True,
)
```

This writes `~/.qiskit/qiskit-ibm.json` (already git-ignored). You only do this once.

> Note: IBM has changed channel names over time (`ibm_quantum`, `ibm_cloud`,
> `ibm_quantum_platform`). If `save_account`/`QiskitRuntimeService()` errors about the
> channel, check the current value on your dashboard's "Connect" snippet and use that.

## 5. Run Shor on hardware

```bash
# Least-busy operational device:
qcrypto shor-demo --backend ibm

# Or target a specific device:
qcrypto shor-demo --backend ibm --ibm-backend ibm_kingston
```

## What to expect (read this first)

**The genuine circuit will most likely NOT cleanly recover the period on hardware.**
That is expected and is the whole lesson of Part 2. Our order-finding circuit, once
transpiled onto a real device's native gates and connectivity, becomes deep enough that
gate errors (~10⁻³ per two-qubit gate) and decoherence wash out the interference peaks
the simulator showed so crisply. You will typically see a broad, noisy histogram rather
than sharp peaks at multiples of 2ᵗ/r.

This is not a failure of the code — it is a measurement of where today's noisy
intermediate-scale quantum (NISQ) hardware actually stands relative to the
fault-tolerant machines a real attack would require. Capture the histogram and compare
it side-by-side with the simulator's (Part 1) — that honest comparison *is* the
deliverable.

## Costs and etiquette

- The Open Plan is time-limited; prefer small `--shots` (e.g. 1024) and avoid repeated
  runs.
- Jobs queue behind other users; a run can take minutes to hours to start.
- Never commit your token. If you suspect it leaked, revoke and regenerate it on the
  dashboard.
