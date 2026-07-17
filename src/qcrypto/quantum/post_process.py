"""Classical post-processing for Shor's algorithm.

This module is deliberately Qiskit-free: everything here is elementary number
theory applied to the *measured* output of the quantum circuit. Isolating it has
two benefits — it is fully unit-testable without a quantum backend, and it makes
explicit that the "quantum" part of Shor produces only one thing (an estimate of
a phase ``s/r``); recovering the order ``r`` and then the factors is classical.

The pipeline is:

    measured integer m  (from the counting register, 0 <= m < 2^t)
      -> phase estimate  m / 2^t  ≈  s / r
      -> continued-fraction convergents  ->  candidate denominators r
      -> verify  a^r ≡ 1 (mod N)
      -> factors  gcd(a^{r/2} ± 1, N)
"""

from __future__ import annotations

import math

__all__ = [
    "continued_fraction_expansion",
    "convergents",
    "candidate_orders",
    "order_from_measurement",
    "factors_from_order",
    "recover_factors_from_counts",
]


def continued_fraction_expansion(numerator: int, denominator: int) -> list[int]:
    """Return the continued-fraction terms [a0, a1, ...] of numerator/denominator."""
    terms: list[int] = []
    while denominator:
        q = numerator // denominator
        terms.append(q)
        numerator, denominator = denominator, numerator - q * denominator
    return terms


def convergents(cf_terms: list[int]) -> list[tuple[int, int]]:
    """Return successive convergents (h_k, k_k) for continued-fraction terms.

    Uses the standard recurrence h_k = a_k h_{k-1} + h_{k-2} (same for k_k).
    """
    result: list[tuple[int, int]] = []
    h_prev2, h_prev1 = 0, 1
    k_prev2, k_prev1 = 1, 0
    for a in cf_terms:
        h = a * h_prev1 + h_prev2
        k = a * k_prev1 + k_prev2
        result.append((h, k))
        h_prev2, h_prev1 = h_prev1, h
        k_prev2, k_prev1 = k_prev1, k
    return result


def candidate_orders(measured: int, n_count: int, modulus: int) -> list[int]:
    """Candidate order denominators from a measured phase, largest first.

    Expands ``measured / 2^n_count`` and returns the convergent denominators that
    could plausibly be the order ``r`` (i.e. 0 < denominator < modulus).
    """
    cf = continued_fraction_expansion(measured, 1 << n_count)
    denoms: list[int] = []
    for _h, k in convergents(cf):
        # k = 1 is the trivial (phase ≈ 0) convergent and carries no order
        # information; excluding it keeps this from degenerating into a brute force.
        if 1 < k < modulus and k not in denoms:
            denoms.append(k)
    return denoms


def order_from_measurement(measured: int, n_count: int, base: int, modulus: int) -> int | None:
    """Recover the order ``r`` of ``base`` mod ``modulus`` from one measurement.

    A convergent may yield only a *divisor* of the true order (when the measured
    ``s`` shares a factor with ``r``), so for each candidate denominator we also
    test small integer multiples until one satisfies ``base^r ≡ 1``.
    """
    if measured == 0:
        return None
    for k in candidate_orders(measured, n_count, modulus):
        multiple = k
        while multiple < modulus:
            if pow(base, multiple, modulus) == 1:
                return multiple
            multiple += k
    return None


def factors_from_order(base: int, order: int | None, modulus: int) -> tuple[int, int] | None:
    """Turn a verified order into non-trivial factors of ``modulus``.

    Returns ``None`` when the order is unusable (odd, or ``base^{r/2} ≡ -1``),
    which is the expected "unlucky" case that simply calls for another shot / base.
    """
    if order is None or order % 2 != 0:
        return None
    root = pow(base, order // 2, modulus)
    if root == 1 or root == modulus - 1:
        return None
    for candidate in (math.gcd(root - 1, modulus), math.gcd(root + 1, modulus)):
        if 1 < candidate < modulus and modulus % candidate == 0:
            return tuple(sorted((candidate, modulus // candidate)))  # type: ignore[return-value]
    return None


def recover_factors_from_counts(
    counts: dict[str, int], base: int, modulus: int, n_count: int
) -> tuple[int, tuple[int, int]] | None:
    """Scan measurement outcomes (most frequent first) for a successful factoring.

    Returns ``(order, (p, q))`` on success, else ``None`` if no outcome yielded a
    usable order — in which case the caller should retry with more shots or a
    different base.
    """
    for bitstring, _freq in sorted(counts.items(), key=lambda kv: -kv[1]):
        measured = int(bitstring.replace(" ", ""), 2)
        order = order_from_measurement(measured, n_count, base, modulus)
        factors = factors_from_order(base, order, modulus)
        if order is not None and factors is not None:
            return order, factors
    return None
