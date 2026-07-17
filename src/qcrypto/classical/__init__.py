"""Classical cryptographic building blocks (Phase 0).

Nothing in this subpackage touches a quantum SDK. It exists so that every
quantum demonstration later in the project has a *correct, well-tested classical
reference* to be compared against — both for validation and for honest
benchmarking ("what did the quantum computer actually save us?").
"""

from __future__ import annotations

from qcrypto.classical.factoring import FactorResult, factor, fermat, pollard_rho, trial_division
from qcrypto.classical.number_theory import (
    egcd,
    is_prime,
    lcm,
    modinv,
)
from qcrypto.classical.rsa import RSAKeyPair, decrypt, encrypt, keypair_from_primes

__all__ = [
    "FactorResult",
    "RSAKeyPair",
    "decrypt",
    "egcd",
    "encrypt",
    "factor",
    "fermat",
    "is_prime",
    "keypair_from_primes",
    "lcm",
    "modinv",
    "pollard_rho",
    "trial_division",
]
