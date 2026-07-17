"""Regenerate the 'exponential wall' figure (docs/article/figures/03-exponential-wall).

This is the reproducible source for the article's headline chart: how many
operations it takes to factor an ``n``-bit modulus, classically vs. with Shor's
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

Implementation note: every quantity is computed in **log10 space**. The raw
operation counts (e.g. 2^1024 for trial division at 2048 bits) exceed the range
of a 64-bit float and would overflow; working with exponents keeps the maths
exact and is exactly what a log-scaled axis displays anyway.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MultipleLocator

FIGURES_DIR = Path(__file__).resolve().parents[1] / "docs" / "article" / "figures"
BIT_SIZES: tuple[int, ...] = (64, 128, 256, 512, 1024, 2048)

_LN10 = math.log(10)


def trial_division_log10(bits: int) -> float:
    """log10 of the naive baseline ~2^(b/2)."""
    return (bits / 2) * math.log10(2)


def gnfs_log10(bits: int) -> float:
    """log10 of the GNFS heuristic complexity L_n[1/3, (64/9)^(1/3)]."""
    ln_n = bits * math.log(2)
    c = (64 / 9) ** (1 / 3)
    natural_log_ops = c * ln_n ** (1 / 3) * math.log(ln_n) ** (2 / 3)
    return natural_log_ops / _LN10


def shor_log10(bits: int) -> float:
    """log10 of the illustrative polynomial (quantum) ~b^3 gate-count."""
    return 3 * math.log10(bits)


def build_figure() -> plt.Figure:
    """Construct the styled figure on a white background (y-axis in log10)."""
    trial = [trial_division_log10(b) for b in BIT_SIZES]
    gnfs = [gnfs_log10(b) for b in BIT_SIZES]
    shor = [shor_log10(b) for b in BIT_SIZES]

    fig, ax = plt.subplots(figsize=(9.2, 5.4), dpi=150)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.plot(BIT_SIZES, trial, color="#dc2626", lw=2.5, marker="o", label="Trial division (naive)")
    ax.plot(BIT_SIZES, gnfs, color="#d97706", lw=2.5, marker="o", label="GNFS (best classical)")
    ax.plot(BIT_SIZES, shor, color="#2563eb", lw=2.5, marker="o", label="Shor (quantum, FT)")

    ax.set_xscale("log", base=2)
    ax.set_xticks(BIT_SIZES)
    ax.set_xticklabels([str(b) for b in BIT_SIZES])

    # y-axis holds log10(operations); label ticks as powers of ten and clip the
    # view at 10^60 so the readable curves aren't crushed by trial division's
    # off-the-chart growth.
    ax.set_ylim(0, 60)
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _pos: f"$10^{{{int(v)}}}$"))

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

    # Annotate the RSA-2048 gap (coordinates are in log10 units).
    ax.annotate(
        "≈$10^{35}$ ops — best classical",
        xy=(2048, gnfs[-1]),
        xytext=(300, 33),
        color="#b45309",
        fontsize=10,
        fontweight="bold",
    )
    ax.annotate(
        "≈$10^{10}$ ops — Shor",
        xy=(2048, shor[-1]),
        xytext=(300, 7),
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
