"""Tests for Shor's classical post-processing (no quantum backend required)."""

from __future__ import annotations

import pytest

from qcrypto.quantum.post_process import (
    candidate_orders,
    continued_fraction_expansion,
    convergents,
    factors_from_order,
    order_from_measurement,
    recover_factors_from_counts,
)


def test_continued_fraction_expansion() -> None:
    assert continued_fraction_expansion(43, 256) == [0, 5, 1, 20, 2]
    assert continued_fraction_expansion(1, 4) == [0, 4]


def test_convergents() -> None:
    assert convergents([0, 5, 1, 20, 2]) == [(0, 1), (1, 5), (1, 6), (21, 125), (43, 256)]


def test_candidate_orders_excludes_trivial_denominator() -> None:
    # k = 1 (trivial phase-0 convergent) must be excluded.
    assert candidate_orders(43, 8, 21) == [5, 6]


@pytest.mark.parametrize(
    ("measured", "n_count", "base", "modulus", "expected"),
    [
        (43, 8, 2, 21, 6),  # order of 2 mod 21 is 6
        (64, 8, 2, 15, 4),  # order of 2 mod 15 is 4
    ],
)
def test_order_from_measurement(
    measured: int, n_count: int, base: int, modulus: int, expected: int
) -> None:
    assert order_from_measurement(measured, n_count, base, modulus) == expected


def test_order_from_measurement_zero_is_none() -> None:
    assert order_from_measurement(0, 8, 2, 21) is None


def test_factors_from_order_success() -> None:
    assert factors_from_order(2, 6, 21) == (3, 7)
    assert factors_from_order(2, 4, 15) == (3, 5)


def test_factors_from_order_rejects_odd_order() -> None:
    assert factors_from_order(2, 5, 21) is None


def test_factors_from_order_rejects_none() -> None:
    assert factors_from_order(2, None, 21) is None


def test_recover_factors_from_counts() -> None:
    # 43 in 8 bits is 0b00101011; make it the dominant outcome.
    counts = {"00101011": 400, "00000000": 120, "10000000": 90}
    recovered = recover_factors_from_counts(counts, base=2, modulus=21, n_count=8)
    assert recovered is not None
    order, factors = recovered
    assert order == 6
    assert set(factors) == {3, 7}


def test_recover_factors_returns_none_on_useless_counts() -> None:
    # Only the all-zero outcome: no order information at all.
    counts = {"00000000": 1000}
    assert recover_factors_from_counts(counts, base=2, modulus=21, n_count=8) is None
