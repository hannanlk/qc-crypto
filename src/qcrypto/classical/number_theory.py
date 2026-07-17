"""Number-theoretic primitives underpinning RSA.

These are written for *clarity first*: RSA's security and mechanics rest entirely
on a handful of elementary results (Bezout's identity, Euler's theorem, the
existence of modular inverses), and the code is meant to be read alongside the
article. Where Python already provides a battle-tested implementation (e.g.
``math.gcd`` and ``pow(a, -1, m)``), we use it, but we also expose the explicit
constructions (extended Euclid) because *seeing the algorithm* is the point.

None of these functions are constant-time. They are for education and for
factoring toy moduli — never for production key material.
"""

from __future__ import annotations

import math
import secrets

__all__ = ["egcd", "modinv", "lcm", "is_prime", "generate_prime"]

# Deterministic Miller-Rabin witness set. Using these exact bases makes the test
# deterministic (no false positives) for every n < 3.317e24, which comfortably
# covers any modulus we generate for demonstrations. Source: well-known result
# on deterministic Miller-Rabin bases.
_DETERMINISTIC_WITNESSES: tuple[int, ...] = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def egcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclidean algorithm.

    Returns ``(g, x, y)`` such that ``a * x + b * y == g == gcd(a, b)``.

    This is the constructive proof of Bezout's identity, and it is *the* reason
    modular inverses exist: if ``gcd(e, phi) == 1`` then ``e * x + phi * y == 1``,
    so ``x`` is the inverse of ``e`` modulo ``phi``.
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t


def modinv(a: int, m: int) -> int:
    """Return the modular inverse of ``a`` modulo ``m``.

    Raises:
        ValueError: if ``a`` is not invertible modulo ``m`` (i.e. gcd != 1).
    """
    g, x, _ = egcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse modulo {m} (gcd={g})")
    return x % m


def lcm(a: int, b: int) -> int:
    """Least common multiple. Used for Carmichael's totient lambda(n)."""
    if a == 0 or b == 0:
        return 0
    return abs(a // math.gcd(a, b) * b)


def is_prime(n: int) -> bool:
    """Deterministic Miller-Rabin primality test for the ranges we use.

    Returns ``True`` iff ``n`` is prime. Deterministic (not probabilistic) for
    all ``n < 3.317 x 10^24`` thanks to the fixed witness set.
    """
    if n < 2:
        return False
    for p in _DETERMINISTIC_WITNESSES:
        if n == p:
            return True
        if n % p == 0:
            return False

    # Write n - 1 = d * 2^r with d odd.
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for a in _DETERMINISTIC_WITNESSES:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits: int) -> int:
    """Generate a random prime with the requested bit length.

    Provided so the article can contrast a *toy* modulus (N = 21) with a
    realistically sized one. Uses :mod:`secrets` for cryptographically strong
    randomness — though, to be explicit: this whole package is educational and
    should not be used to generate real keys.

    Args:
        bits: Desired bit length (>= 2). The top bit is forced so the prime has
            exactly ``bits`` bits; the low bit is forced so it is odd.
    """
    if bits < 2:
        raise ValueError("bits must be >= 2")
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_prime(candidate):
            return candidate
