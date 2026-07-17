# qcrypto — Quantum Computing vs. Cryptography

A hands-on, **honest** tour of how quantum computing affects modern cryptography.
We break a toy RSA key with Shor's algorithm, show why Grover's algorithm only
dents symmetric crypto rather than shattering it, and end at the NIST-standardised
post-quantum algorithm (ML-KEM) that replaces RSA — all while carefully
separating *what runs on a simulator today* from *what a fault-tolerant machine
could do tomorrow*.

> **Status:** Phase 0 (classical foundation). The repository is private while the
> Shor implementation (Phase 1) is polished.

## Why this project exists

Most "quantum breaks RSA" content is either hand-wavy or quietly dishonest (for
example, factoring 15 or 21 with a circuit that was pre-simplified using the
answer). This project holds itself to a higher bar: every quantum result is
compared against a classical baseline, hardware limitations are stated plainly,
and no capability is exaggerated. The intended audience is software engineers,
cybersecurity professionals, CS students, and researchers.

## The narrative arc

| Phase | Theme | Status |
|------:|-------|--------|
| **0** | Why RSA works; classical factoring baselines | ✅ done |
| **1** | Shor's algorithm on a simulator (period-finding → factors) | 🔨 in progress |
| 2 | Shor on real IBM Quantum hardware (reduced/compiled, honestly framed) | planned |
| 3 | Grover's algorithm and why AES survives | planned |
| 4 | ML-KEM (FIPS 203) — the post-quantum replacement | planned |

Each phase ships code, tests, diagrams, and a matching section of the companion
article in [`docs/article/`](docs/article/).

## Install

```bash
git clone https://github.com/hannan/RSA-qc.git
cd RSA-qc
python -m pip install -e ".[dev]"          # classical foundation + dev tooling
# The quantum stack arrives in Phase 1:
# python -m pip install -e ".[dev,quantum]"
```

Requires Python 3.10+.

## Try it

```bash
# Walk through RSA end to end on the toy modulus n = 21,
# then break it classically by factoring n and recovering the private key:
qcrypto rsa-demo

# Factor an integer with a chosen classical method and see the timing:
qcrypto factor 8051 --method pollard_rho
```

Phase 1 (Shor on the Aer simulator) needs the quantum extra:

```bash
python -m pip install -e ".[quantum]"

# Factor N = 21 with Shor's algorithm, stage by stage:
qcrypto shor-demo
```

## Project layout

```
src/qcrypto/
  classical/        # Phase 0: number theory, textbook RSA, classical factoring
  cli.py            # staged, one-panel-per-step Rich CLI
  _logging.py       # opt-in Rich logging (library never configures logging itself)
tests/              # pytest suite (classical only; deterministic, fast)
docs/article/       # the companion article, written alongside the code
.github/workflows/  # CI: ruff + mypy + pytest on 3.10–3.12 (no quantum in CI)
```

## Development

```bash
ruff check . && ruff format --check .   # lint + format
mypy                                    # strict type checking (src/)
pytest --cov=qcrypto                     # tests with coverage
```

## A note on scope and honesty

This is educational software. The RSA implementation is *schoolbook* RSA with no
padding or side-channel protection — never use it for real key material. The
quantum demonstrations (from Phase 1) target toy moduli on simulators and small
hardware; they illustrate the algorithms, they do **not** threaten real keys. The
gap between the two is not a footnote in this project — it is the whole point.

## License

MIT — see [LICENSE](LICENSE).
