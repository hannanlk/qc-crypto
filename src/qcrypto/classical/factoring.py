"""Classical integer factorisation baselines.

Why this module exists: before we ever touch a quantum computer, we need an
honest classical yardstick. These routines factor the same toy moduli Shor will
target, so the article can make a *fair* comparison and avoid the usual hype
("quantum factored 21!") without noting that a wristwatch factors 21 instantly.

Three methods of increasing sophistication are included so the reader can see the
classical landscape Shor is competing against:

* ``trial_division`` — O(sqrt(n)); the naive baseline.
* ``fermat``         — fast when the two prime factors are close together.
* ``pollard_rho``    — sub-exponential-ish heuristic; the workhorse for
  moderate composites and the honest "classical is not helpless" counterpoint.

All of these remain fully exponential in the number of *digits*, which is the
whole reason RSA is believed hard — and the gap Shor's polynomial-time algorithm
would close on a fault-tolerant machine.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

from qcrypto._logging import get_logger

logger = get_logger("factoring")

__all__ = ["FactorResult", "trial_division", "fermat", "pollard_rho", "factor"]


@dataclass(frozen=True)
class FactorResult:
    """Outcome of a factorisation attempt.

    Attributes:
        n:                The number that was factored.
        factors:          The two non-trivial factors as a sorted tuple.
        method:           Human-readable name of the algorithm used.
        elapsed_seconds:  Wall-clock time taken (for benchmarking against Shor).
        iterations:       Main-loop iteration count, where meaningful.
    """

    n: int
    factors: tuple[int, int]
    method: str
    elapsed_seconds: float
    iterations: int | None = None

    def verify(self) -> bool:
        """Confirm the factors actually multiply back to ``n``."""
        p, q = self.factors
        return p * q == self.n


def trial_division(n: int) -> FactorResult:
    """Factor ``n`` by trial division up to ``sqrt(n)``.

    Raises:
        ValueError: if ``n`` has no factor <= sqrt(n) (e.g. ``n`` is prime).
    """
    start = time.perf_counter()
    iterations = 0
    limit = math.isqrt(n)
    d = 2
    while d <= limit:
        iterations += 1
        if n % d == 0:
            elapsed = time.perf_counter() - start
            return FactorResult(n, _sorted(d, n // d), "trial_division", elapsed, iterations)
        d += 1 if d == 2 else 2  # test 2, then only odd candidates
    raise ValueError(f"no non-trivial factor of {n} found by trial division (prime?)")


def fermat(n: int) -> FactorResult:
    """Fermat's factorisation: write ``n = a^2 - b^2 = (a - b)(a + b)``.

    Extremely fast when ``n``'s factors are close to ``sqrt(n)`` (the failure
    mode that makes choosing nearby RSA primes dangerous), slow otherwise.

    Raises:
        ValueError: if ``n`` is even (caller should strip factors of 2 first).
    """
    if n % 2 == 0:
        raise ValueError("fermat() expects an odd integer")
    start = time.perf_counter()
    a = math.isqrt(n)
    if a * a < n:
        a += 1
    iterations = 0
    while True:
        iterations += 1
        b2 = a * a - n
        b = math.isqrt(b2)
        if b * b == b2:
            elapsed = time.perf_counter() - start
            return FactorResult(n, _sorted(a - b, a + b), "fermat", elapsed, iterations)
        a += 1


def pollard_rho(n: int, *, c: int = 1, max_iterations: int = 1_000_000) -> FactorResult:
    """Pollard's rho with Floyd cycle detection and ``g(x) = x^2 + c mod n``.

    Returns a factorisation of a *composite* ``n``. If the chosen constant ``c``
    yields the trivial factor ``n`` (a known failure mode), the caller can retry
    with a different ``c``; :func:`factor` does this automatically.

    Raises:
        ValueError: if ``n`` is even, prime, or no factor is found in
            ``max_iterations`` steps.
    """
    if n % 2 == 0:
        raise ValueError("pollard_rho() expects an odd integer")
    start = time.perf_counter()

    def g(x: int) -> int:
        return (x * x + c) % n

    x, y, d = 2, 2, 1
    iterations = 0
    while d == 1:
        iterations += 1
        if iterations > max_iterations:
            raise ValueError(f"pollard_rho exceeded {max_iterations} iterations for n={n}")
        x = g(x)
        y = g(g(y))
        d = math.gcd(abs(x - y), n)
    if d == n:
        raise ValueError(f"pollard_rho found only the trivial factor for n={n}, c={c}")
    elapsed = time.perf_counter() - start
    return FactorResult(n, _sorted(d, n // d), "pollard_rho", elapsed, iterations)


def factor(n: int, method: str = "auto") -> FactorResult:
    """Factor a semiprime ``n`` using the requested method.

    Args:
        n:      The composite to factor (intended: a product of two primes).
        method: One of ``"trial_division"``, ``"fermat"``, ``"pollard_rho"`` or
                ``"auto"``. ``"auto"`` uses Pollard's rho (retrying ``c`` on the
                trivial-factor failure mode) and falls back to trial division.

    Raises:
        ValueError: for an invalid ``method`` or if factorisation fails.
    """
    if n < 4:
        raise ValueError("n must be a composite >= 4")

    if method == "trial_division":
        return trial_division(n)
    if method == "fermat":
        return fermat(n)
    if method == "pollard_rho":
        return pollard_rho(n)
    if method != "auto":
        raise ValueError(f"unknown method {method!r}")

    # auto: even numbers are trivial; otherwise try Pollard's rho across a few
    # constants, then fall back to the always-correct (if slow) trial division.
    if n % 2 == 0:
        return FactorResult(n, _sorted(2, n // 2), "trial_division", 0.0, 1)
    for c in (1, 2, 3, 5, 7):
        try:
            return pollard_rho(n, c=c)
        except ValueError:
            logger.debug("pollard_rho failed for n=%d with c=%d; retrying", n, c)
    return trial_division(n)


def _sorted(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a <= b else (b, a)
