"""Regenerate the Phase 3 (Grover) figures from real seeded runs.

Requires the quantum extra:  pip install -e ".[quantum]"

Usage:
    python scripts/make_grover_figures.py

Outputs (docs/article/figures/):
    07-grover-iterations.png   success probability vs. iteration count
    08-grover-histogram.png    measurement histogram at the optimal iteration
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt

from qcrypto.quantum.grover import optimal_iterations, search

FIGURES_DIR = Path(__file__).resolve().parents[1] / "docs" / "article" / "figures"

N_QUBITS = 4
MARKED = 9
SHOTS = 2048
SEED = 42

_BLUE = "#2563eb"
_AMBER = "#d97706"
_GREEN = "#16a34a"


def analytic_success(iterations: int, n_qubits: int, num_marked: int = 1) -> float:
    """P(success) = sin^2((2k+1)·θ), θ = arcsin(√(M/N)). The Grover oscillation."""
    theta = math.asin(math.sqrt(num_marked / (1 << n_qubits)))
    return math.sin((2 * iterations + 1) * theta) ** 2


def make_iterations_figure() -> None:
    max_iter = 8
    ks = list(range(max_iter + 1))
    analytic = [analytic_success(k, N_QUBITS) for k in ks]
    simulated = [search(N_QUBITS, MARKED, iterations=k, shots=SHOTS, seed=SEED).success_probability
                 for k in ks]
    best = optimal_iterations(N_QUBITS, 1)

    fig, ax = plt.subplots(figsize=(9.0, 5.0), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.plot(ks, analytic, color=_BLUE, lw=2.5, label="analytic  sin²((2k+1)θ)")
    ax.scatter(ks, simulated, color=_AMBER, zorder=5, s=45, label="simulated (Aer)")
    ax.axvline(best, color=_GREEN, ls="--", lw=1.5, label=f"optimal k = {best}")

    ax.set_xlabel("Grover iterations k", fontsize=12, fontweight="bold")
    ax.set_ylabel("P(measure the marked item)", fontsize=12, fontweight="bold")
    ax.set_title(
        f"Grover amplitude amplification  ·  1 marked item in 2^{N_QUBITS} = {1 << N_QUBITS}",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_ylim(0, 1.05)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.grid(True, color="#eef2f7", lw=1)
    ax.legend(frameon=False, fontsize=10, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "07-grover-iterations.png", dpi=150, facecolor="white")
    plt.close(fig)


def make_histogram_figure() -> None:
    result = search(N_QUBITS, MARKED, shots=SHOTS, seed=SEED)
    states = sorted(result.counts, key=lambda b: int(b.replace(" ", ""), 2))
    xs = [int(b.replace(" ", ""), 2) for b in states]
    ys = [result.counts[b] for b in states]
    colors = [_AMBER if x == MARKED else _BLUE for x in xs]

    fig, ax = plt.subplots(figsize=(9.0, 5.0), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.bar(xs, ys, color=colors)
    ax.set_xlabel("measured item", fontsize=12, fontweight="bold")
    ax.set_ylabel(f"counts (of {SHOTS} shots)", fontsize=12, fontweight="bold")
    ax.set_title(
        f"Grover result  ·  marked item {MARKED} amplified to "
        f"{result.success_probability:.0%}",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(range(1 << N_QUBITS))
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "08-grover-histogram.png", dpi=150, facecolor="white")
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    make_iterations_figure()
    make_histogram_figure()
    print(f"wrote {FIGURES_DIR / '07-grover-iterations.png'}")
    print(f"wrote {FIGURES_DIR / '08-grover-histogram.png'}")


if __name__ == "__main__":
    main()
