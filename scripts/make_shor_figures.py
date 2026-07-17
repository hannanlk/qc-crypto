"""Regenerate the Phase 1 figures: the Shor order-finding circuit and its
measurement histogram, from a real seeded simulator run (N = 21, a = 2).

Requires the quantum extra:  pip install -e ".[quantum]"

Usage:
    python scripts/make_shor_figures.py

Outputs (docs/article/figures/):
    04-shor-circuit.png       the order-finding circuit (high level)
    05-shor-histogram.png     measurement outcomes with expected phase peaks

Everything is seeded so the figures match the numbers quoted in the article.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from qcrypto.backends import run_counts
from qcrypto.quantum.shor import build_order_finding_circuit, default_counting_qubits

FIGURES_DIR = Path(__file__).resolve().parents[1] / "docs" / "article" / "figures"

MODULUS = 21
BASE = 2
SHOTS = 2048
SEED = 42

_BLUE = "#2563eb"
_AMBER = "#d97706"


def make_circuit_figure(n_count: int) -> None:
    """Draw the order-finding circuit and save it."""
    circuit = build_order_finding_circuit(BASE, MODULUS, n_count)
    fig = circuit.draw(
        output="mpl",
        fold=-1,
        style={"backgroundcolor": "#ffffff"},
    )
    fig.suptitle(
        f"Shor order-finding circuit  ·  N={MODULUS}, a={BASE}, "
        f"{n_count} counting + {MODULUS.bit_length()} work qubits",
        fontsize=12,
        fontweight="bold",
    )
    fig.savefig(FIGURES_DIR / "04-shor-circuit.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def make_histogram_figure(n_count: int) -> None:
    """Run the circuit on Aer and plot the measurement histogram."""
    circuit = build_order_finding_circuit(BASE, MODULUS, n_count)
    counts = run_counts(circuit, shots=SHOTS, backend="aer", seed=SEED)

    measured = {int(b.replace(" ", ""), 2): c for b, c in counts.items()}
    xs = sorted(measured)
    ys = [measured[x] for x in xs]

    fig, ax = plt.subplots(figsize=(9.2, 5.0), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.bar(xs, ys, width=6, color=_BLUE, label="measured counts")

    # Expected phase peaks at k · 2^t / r for the true order r = 6.
    period = 6
    scale = (1 << n_count) / period
    for k in range(period):
        peak = round(k * scale)
        ax.axvline(peak, color=_AMBER, ls="--", lw=1, alpha=0.8)
    ax.axvline(0, color=_AMBER, ls="--", lw=1, alpha=0.8, label="expected peaks  k·2ᵗ/6")

    ax.set_xlabel("measured value m  (counting register)", fontsize=12, fontweight="bold")
    ax.set_ylabel(f"counts (of {SHOTS} shots)", fontsize=12, fontweight="bold")
    ax.set_title(
        f"Shor measurement histogram  ·  N={MODULUS}, a={BASE}  →  order r=6",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xlim(-10, 1 << n_count)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.legend(frameon=False, fontsize=10)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "05-shor-histogram.png", dpi=150, facecolor="white")
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    n_count = default_counting_qubits(MODULUS)
    make_circuit_figure(n_count)
    make_histogram_figure(n_count)
    print(f"wrote {FIGURES_DIR / '04-shor-circuit.png'}")
    print(f"wrote {FIGURES_DIR / '05-shor-histogram.png'}")


if __name__ == "__main__":
    main()
