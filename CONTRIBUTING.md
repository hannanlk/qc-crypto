# Contributing

Thanks for your interest. This is primarily an educational, portfolio-quality project,
so the bar for contributions is *clarity and correctness* as much as functionality.

## Principles

1. **Correctness over hype.** Claims about quantum capability must be accurate and, where
   relevant, distinguish simulator results from real hardware and near-term from
   fault-tolerant regimes.
2. **Every quantum result has a classical baseline.** New algorithm demos should be
   comparable against a classical reference.
3. **Explain the *why*.** Docstrings and article prose should justify design decisions,
   not just describe them.

## Development setup

```bash
python -m pip install -e ".[dev,quantum,pqc]"
python -m ruff format .
python -m ruff check .
python -m mypy
python -m pytest
```

- Code is formatted and linted with **ruff**, type-checked with **mypy** (strict), and
  tested with **pytest**.
- The quantum tests auto-skip when Qiskit/Aer are absent; PQC tests auto-skip without
  `kyber-py`. CI runs the classical suite only (fast and deterministic).
- Please keep functions typed and documented, and add tests for new behaviour.

## Scope reminder

The cryptographic code here is *educational* (schoolbook RSA, wrapped reference ML-KEM)
and is not constant-time or side-channel hardened. Please do not add anything that
implies it is production-secure.
