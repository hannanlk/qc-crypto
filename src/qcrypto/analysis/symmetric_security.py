"""How Grover's algorithm actually affects symmetric ciphers — without the hype.

The lazy headline is "Grover halves AES key strength, so AES-128 is broken." Both
clauses are misleading. This module encodes the accurate picture so the article and
CLI quote consistent, defensible numbers.

Key points, in order of importance:

1. Grover turns a brute-force search over 2^k keys into ~2^(k/2) *queries*. It
   halves the *exponent*, not the security outright.
2. That halving is a worst-case *query* bound. Grover is inherently sequential —
   its ~2^(k/2) iterations cannot be meaningfully parallelised the way classical
   brute force can (Zalka; and NIST's PQC rationale). So the wall-clock cost of a
   real attack is far worse than "2^(k/2) operations" suggests.
3. Consequently NIST treats AES-128 as still providing meaningful post-quantum
   security (Category 1) and AES-256 as solidly post-quantum (Category 5). The
   practical mitigation is trivial: use a larger key. There is no analogue of
   Shor that collapses symmetric security.

Contrast this with RSA, where Shor is exponential and doubling the key size does
*not* save you — that asymmetry is the spine of the whole series.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["CipherSecurity", "grover_security_table"]


@dataclass(frozen=True)
class CipherSecurity:
    """Security of a symmetric cipher against classical vs. Grover attacks.

    Attributes:
        name: Cipher/key-size label (e.g. "AES-128").
        key_bits: Key length in bits = classical brute-force security.
        grover_bits: Idealised Grover query exponent = key_bits // 2.
        nist_pq_category: NIST post-quantum security category (1, 3, or 5).
        verdict: Short plain-language assessment.
    """

    name: str
    key_bits: int
    grover_bits: int
    nist_pq_category: int
    verdict: str


def grover_security_table() -> list[CipherSecurity]:
    """Return the classical-vs-Grover picture for the AES family."""
    return [
        CipherSecurity(
            name="AES-128",
            key_bits=128,
            grover_bits=64,
            nist_pq_category=1,
            verdict="Idealised Grover gives 2^64 queries, but they are sequential and "
            "non-parallelisable; still considered acceptable post-quantum (NIST Cat. 1).",
        ),
        CipherSecurity(
            name="AES-192",
            key_bits=192,
            grover_bits=96,
            nist_pq_category=3,
            verdict="2^96 effective query exponent — comfortably secure.",
        ),
        CipherSecurity(
            name="AES-256",
            key_bits=256,
            grover_bits=128,
            nist_pq_category=5,
            verdict="2^128 effective query exponent — solidly post-quantum secure (NIST Cat. 5).",
        ),
    ]
