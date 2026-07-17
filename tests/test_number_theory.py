"""Tests for the number-theoretic primitives."""

from __future__ import annotations

import math

import pytest

from qcrypto.classical.number_theory import (
    egcd,
    generate_prime,
    is_prime,
    lcm,
    modinv,
)


@pytest.mark.parametrize(
    ("a", "b"),
    [(240, 46), (17, 5), (0, 7), (7, 0), (1071, 462), (65537, 3120)],
)
def test_egcd_satisfies_bezout(a: int, b: int) -> None:
    g, x, y = egcd(a, b)
    assert g == math.gcd(a, b)
    assert a * x + b * y == g


@pytest.mark.parametrize(("a", "m"), [(3, 7), (5, 12), (65537, 3120), (2, 21)])
def test_modinv_roundtrip(a: int, m: int) -> None:
    inv = modinv(a, m)
    assert (a * inv) % m == 1


def test_modinv_raises_when_not_coprime() -> None:
    with pytest.raises(ValueError):
        modinv(6, 9)  # gcd(6, 9) = 3


def test_lcm() -> None:
    assert lcm(4, 6) == 12
    assert lcm(2, 6) == 6  # Carmichael lambda for n = 21
    assert lcm(0, 5) == 0


@pytest.mark.parametrize("n", [2, 3, 5, 7, 11, 13, 97, 3, 7, 7919, 104729])
def test_is_prime_true(n: int) -> None:
    assert is_prime(n)


@pytest.mark.parametrize("n", [-1, 0, 1, 4, 21, 100, 561, 1105])  # incl. Carmichael numbers
def test_is_prime_false(n: int) -> None:
    assert not is_prime(n)


def test_is_prime_matches_reference_up_to_2000() -> None:
    def naive(n: int) -> bool:
        if n < 2:
            return False
        return all(n % d for d in range(2, math.isqrt(n) + 1))

    for n in range(2000):
        assert is_prime(n) == naive(n), n


@pytest.mark.parametrize("bits", [8, 16, 32])
def test_generate_prime_has_requested_bit_length(bits: int) -> None:
    p = generate_prime(bits)
    assert is_prime(p)
    assert p.bit_length() == bits
