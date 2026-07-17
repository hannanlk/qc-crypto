"""Textbook RSA — deliberately simple, deliberately insecure.

This is *schoolbook* RSA on integers: no OAEP padding, no constant-time
operations, no side-channel hardening. That is intentional. The goal is to make
the mathematics visible so the reader can watch Shor's algorithm dismantle it in
later phases. For anything real, use a vetted library (e.g. ``cryptography``).

The central teaching thesis of the whole project lives here:

    RSA's private key is recoverable *the instant you can factor the modulus*.

``keypair_from_primes`` and :func:`recover_private_exponent` make that explicit:
given ``p`` and ``q`` (what a factoring algorithm outputs) plus the public ``e``,
reconstructing the private ``d`` is elementary classical arithmetic. Shor does not
"decrypt" anything — it factors, and factoring is the whole ballgame.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from qcrypto._logging import get_logger
from qcrypto.classical.number_theory import generate_prime, is_prime, modinv

logger = get_logger("rsa")

__all__ = [
    "RSAKeyPair",
    "keypair_from_primes",
    "generate_keypair",
    "recover_private_exponent",
    "encrypt",
    "decrypt",
]

# Default public exponent used for realistically sized keys. 65537 (0x10001) is
# the near-universal choice: it is prime and has only two set bits, making
# encryption fast, while being large enough to avoid small-exponent pitfalls.
DEFAULT_E = 65537


@dataclass(frozen=True)
class RSAKeyPair:
    """An RSA key pair together with the secret factorisation.

    We keep ``p`` and ``q`` on the object because this is a *teaching* artifact:
    in the real world the whole point is that ``p`` and ``q`` are destroyed after
    key generation. Here we retain them so demonstrations can show the attacker's
    goal (recovering them) explicitly.

    Attributes:
        p, q: The secret prime factors.
        e:    Public exponent.
        d:    Private exponent, the inverse of ``e`` modulo ``phi(n)``.
        n:    Public modulus, ``p * q``.
        phi:  Euler's totient ``(p - 1) * (q - 1)``.
    """

    p: int
    q: int
    e: int
    d: int

    @property
    def n(self) -> int:
        return self.p * self.q

    @property
    def phi(self) -> int:
        return (self.p - 1) * (self.q - 1)

    @property
    def public_key(self) -> tuple[int, int]:
        """The pair ``(n, e)`` an encryptor would be given."""
        return self.n, self.e

    @property
    def private_key(self) -> tuple[int, int]:
        """The pair ``(n, d)`` the holder keeps secret."""
        return self.n, self.d

    @property
    def exponents_coincide(self) -> bool:
        """True when ``e == d`` — an artifact of very small moduli.

        For N = 21, phi = 12 whose multiplicative group has exponent 2, so every
        valid public exponent is its own inverse and ``e == d``. This never
        happens for realistically sized keys and is flagged so readers do not
        over-generalise from the toy example.
        """
        return self.e == self.d


def keypair_from_primes(p: int, q: int, e: int | None = None) -> RSAKeyPair:
    """Construct an RSA key pair from two primes and an optional public exponent.

    Args:
        p, q: Distinct primes.
        e:    Public exponent. If ``None``, the smallest integer >= 3 that is
              coprime to ``phi(n)`` is chosen (keeps toy examples readable).

    Raises:
        ValueError: if ``p``/``q`` are not distinct primes, or ``e`` is invalid.
    """
    if not is_prime(p) or not is_prime(q):
        raise ValueError(f"p and q must both be prime (got p={p}, q={q})")
    if p == q:
        raise ValueError("p and q must be distinct")

    phi = (p - 1) * (q - 1)

    if e is None:
        e = _smallest_valid_exponent(phi)
    elif not (1 < e < phi and math.gcd(e, phi) == 1):
        raise ValueError(f"e={e} must satisfy 1 < e < phi(n)={phi} and gcd(e, phi)=1")

    d = modinv(e, phi)
    pair = RSAKeyPair(p=p, q=q, e=e, d=d)
    logger.debug("Built RSA key pair n=%d e=%d d=%d (phi=%d)", pair.n, e, d, phi)
    if pair.exponents_coincide:
        logger.info("e == d for n=%d: small-modulus artifact, not a real-world property", pair.n)
    return pair


def generate_keypair(bits: int = 2048, e: int = DEFAULT_E) -> RSAKeyPair:
    """Generate a realistically structured key pair (two ~``bits/2``-bit primes).

    Not for production use, but useful for the article's "what real RSA looks
    like" contrast against the N = 21 toy.
    """
    if bits < 8:
        raise ValueError("bits must be >= 8 for a non-degenerate two-prime modulus")
    half = bits // 2
    while True:
        p = generate_prime(half)
        q = generate_prime(bits - half)
        if p == q:
            continue
        phi = (p - 1) * (q - 1)
        if math.gcd(e, phi) == 1:
            return RSAKeyPair(p=p, q=q, e=e, d=modinv(e, phi))


def recover_private_exponent(n: int, e: int, p: int, q: int) -> int:
    """Reconstruct the private exponent ``d`` from a *factored* modulus.

    This is the punchline of Phase 0: once an attacker has ``p`` and ``q`` (the
    output of any factoring routine, classical or Shor's), recovering ``d`` is a
    single modular inverse. There is no additional "quantum decryption" step.

    Raises:
        ValueError: if ``p * q != n``.
    """
    if p * q != n:
        raise ValueError(f"p*q={p * q} does not equal n={n}; not a valid factorisation")
    phi = (p - 1) * (q - 1)
    return modinv(e, phi)


def encrypt(message: int, public_key: tuple[int, int]) -> int:
    """Encrypt an integer message: ``c = m^e mod n``.

    Raises:
        ValueError: if ``message`` is outside ``[0, n)``.
    """
    n, e = public_key
    if not 0 <= message < n:
        raise ValueError(f"message must be in [0, n)={n}; got {message}")
    return pow(message, e, n)


def decrypt(ciphertext: int, private_key: tuple[int, int]) -> int:
    """Decrypt an integer ciphertext: ``m = c^d mod n``."""
    n, d = private_key
    if not 0 <= ciphertext < n:
        raise ValueError(f"ciphertext must be in [0, n)={n}; got {ciphertext}")
    return pow(ciphertext, d, n)


def _smallest_valid_exponent(phi: int) -> int:
    """Smallest ``e >= 3`` coprime to ``phi`` (keeps toy demos legible)."""
    e = 3
    while math.gcd(e, phi) != 1:
        e += 2
    if e >= phi:
        raise ValueError(f"no valid public exponent < phi={phi}")
    return e
