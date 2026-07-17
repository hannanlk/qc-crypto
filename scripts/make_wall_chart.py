"""Regenerate the 'exponential wall' figure (docs/article/figures/03-exponential-wall).

This is the reproducible source for the article's headline chart: the number of
operations needed to factor an ``n``-bit modulus, classically vs. with Shor's
algorithm. The committed SVG is a hand-tuned rendering of exactly these numbers;
run this script to regenerate raster/vector versions or to tweak the model.

Requires matplotlib:  ``pip install matplotlib``

Usage:
    python scripts/make_wall_chart.py

Modelling notes (all heuristic — the *shape* is the point, not 3-sig-fig cost):

* Trial division: ~2^(b/2) operations (you test divisors up to sqrt(n) = 2^(b/2)).
* GNFS (General Number Field Sieve), the best known *classical* factoring
  algorithm: sub-exponential complexity L_n[1/3, (64/9)^(1/3)] =
  exp( (64/9)^(1/3) * (ln n)^(1/3) * (ln ln n)^(2/3) ).
* Shor's algorithm: polynomial; we use a ~b^3 gate-count scaling as an
  illustrative stand-in (true circuits are ~b^2 log b to b^3 depending on the
  arithmetic). This is deliberately schematic and labelled as such.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator

FIGURES_DIR = Path(__file__).resolve().parents[1] / "docs" / "article" / "figures"
BIT_SIZES: tuple[int, ...] = (64, 128, 256, 512, 1024, 2048)


def trial_division_ops(bits: int) -> float:
    """Naive baseline: ~2^(b/2) operations."""
    return 2.0 ** (bits / 2)


def gnfs_ops(bits: int) -> float:
    """Best known classical: L_n[1/3, (64/9)^(1/3)]."""
    ln_n = bits * math.log(2)
    c = (64 / 9) ** (1 / 3)
    return math.exp(c * ln_n ** (1 / 3) * math.log(ln_n) ** (2 / 3))


def shor_ops(bits: int) -> float:
    """Illustrative polynomial (quantum) gate-count scaling, ~b^3."""
    return float(bits) ** 3


def build_figure() -> plt.Figure:
    """Construct the styled figure on a white background."""
    trial = [trial_division_ops(b) for b in BIT_SIZES]
    gnfs = [gnfs_ops(b) for b in BIT_SIZES]
    shor = [shor_ops(b) for b in BIT_SIZES]

    fig, ax = plt.subplots(figsize=(9.2, 5.4), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.plot(BIT_SIZES, trial, color="#dc2626", lw=2.5, marker="o", label="Trial division (naive)")
    ax.plot(BIT_SIZES, gnfs, color="#d97706", lw=2.5, marker="o", label="GNFS (best classical)")
    ax.plot(BIT_SIZES, shor, color="#2563eb", lw=2.5, marker="o", label="Shor (quantum, FT)")

    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xticks(BIT_SIZES)
    ax.set_xticklabels([str(b) for b in BIT_SIZES])
    ax.set_ylim(1, 1e60)
    ax.yaxis.set_major_locator(LogLocator(base=10, numticks=7))

    ax.set_xlabel("modulus size (bits)", fontsize=12, fontweight="bold")
    ax.set_ylabel("operations to factor (log scale)", fontsize=12, fontweight="bold")
    ax.set_title(
        "Why RSA Is Safe Today — and What Shor Would Change",
        fontsize=15,
        fontweight="bold",
        pad=14,
    )

    ax.grid(True, which="major", color="#eef2f7", lw=1)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    # Annotate the RSA-2048 gap.
    ax.annotate(
        "≈10³⁵ ops — best classical",
        xy=(2048, gnfs[-1]),
        xytext=(300, 1e33),
        color="#b45309",
        fontsize=10,
        fontweight="bold",
    )
    ax.annotate(
        "≈10¹⁰ ops — Shor",
        xy=(2048, shor[-1]),
        xytext=(300, 1e7),
        color="#1d4ed8",
        fontsize=10,
        fontweight="bold",
    )
    ax.legend(frameon=False, fontsize=11, loc="upper left")

    fig.text(
        0.02,
        -0.02,
        "Heuristic scalings; the shape is the point: classical cost explodes "
        "super-polynomially with key size, Shor's stays polynomial.",
        fontsize=9,
        color="#94a3b8",
    )
    fig.tight_layout()
    return fig


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig = build_figure()
    png_path = FIGURES_DIR / "03-exponential-wall.png"
    svg_path = FIGURES_DIR / "03-exponential-wall.generated.svg"
    fig.savefig(png_path, bbox_inches="tight", facecolor="white")
    fig.savefig(svg_path, bbox_inches="tight", facecolor="white")
    print(f"wrote {png_path}")
    print(f"wrote {svg_path}")


if __name__ == "__main__":
    main()
