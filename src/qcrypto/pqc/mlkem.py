"""ML-KEM (FIPS 203) — the post-quantum replacement for RSA/ECC key exchange.

ML-KEM is a *key-encapsulation mechanism* (KEM), not a drop-in for RSA encryption.
The pattern is: the receiver publishes an encapsulation key; a sender uses it to
produce a ciphertext and a shared secret; the receiver decapsulates the ciphertext
to recover the same shared secret. That shared secret then keys a symmetric cipher
(e.g. AES-256, which — see Part 3 — is itself quantum-safe).

Its security rests on the hardness of the Module Learning-With-Errors (MLWE)
problem. Crucially — and this is a point the article makes carefully — lattice
problems resist *all known* quantum algorithms; there is no proof they are
quantum-hard, only the (strong) absence of an efficient quantum attack plus
worst-case-to-average-case reductions. We are precise about "no known attack" vs.
"proven secure".

Implementation boundary: the cryptography here is delegated to the ``kyber-py``
reference implementation. This module only orchestrates a round trip and records
sizes for teaching. ``kyber-py`` is educational and not side-channel hardened; do
not use any of this for real key material — use a vetted library such as
``liboqs``/``oqs`` or a platform-native ML-KEM.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "MLKEMParameterSet",
    "PARAMETER_SETS",
    "KEMRoundTrip",
    "run_roundtrip",
    "parameter_table",
]


@dataclass(frozen=True)
class MLKEMParameterSet:
    """FIPS 203 parameter set with its standardised object sizes (in bytes).

    Attributes:
        name: e.g. ``"ML-KEM-768"``.
        nist_level: NIST post-quantum security category (1, 3, or 5).
        ek_bytes: Encapsulation (public) key size.
        dk_bytes: Decapsulation (secret) key size.
        ct_bytes: Ciphertext size.
        shared_secret_bytes: Shared secret size (always 32 = 256 bits).
    """

    name: str
    nist_level: int
    ek_bytes: int
    dk_bytes: int
    ct_bytes: int
    shared_secret_bytes: int = 32


# Sizes are fixed by FIPS 203.
PARAMETER_SETS: dict[str, MLKEMParameterSet] = {
    "ML-KEM-512": MLKEMParameterSet("ML-KEM-512", nist_level=1, ek_bytes=800, dk_bytes=1632, ct_bytes=768),
    "ML-KEM-768": MLKEMParameterSet("ML-KEM-768", nist_level=3, ek_bytes=1184, dk_bytes=2400, ct_bytes=1088),
    "ML-KEM-1024": MLKEMParameterSet("ML-KEM-1024", nist_level=5, ek_bytes=1568, dk_bytes=3168, ct_bytes=1568),
}


@dataclass
class KEMRoundTrip:
    """The observable result of one encapsulate/decapsulate round trip."""

    parameter_set: MLKEMParameterSet
    ek_len: int
    dk_len: int
    ct_len: int
    shared_secret_sender: bytes
    shared_secret_receiver: bytes

    @property
    def agreed(self) -> bool:
        """True iff both parties derived the identical shared secret."""
        return self.shared_secret_sender == self.shared_secret_receiver

    @property
    def sizes_match_standard(self) -> bool:
        """True iff observed key/ciphertext sizes match the FIPS 203 constants."""
        p = self.parameter_set
        return (self.ek_len, self.dk_len, self.ct_len) == (p.ek_bytes, p.dk_bytes, p.ct_bytes)


def _implementation(name: str) -> object:
    """Return the kyber-py ML-KEM object for a parameter-set name (lazy import)."""
    from kyber_py.ml_kem import ML_KEM_512, ML_KEM_768, ML_KEM_1024

    table = {
        "ML-KEM-512": ML_KEM_512,
        "ML-KEM-768": ML_KEM_768,
        "ML-KEM-1024": ML_KEM_1024,
    }
    if name not in table:
        raise ValueError(f"unknown parameter set {name!r}; choose from {sorted(table)}")
    return table[name]


def run_roundtrip(name: str = "ML-KEM-768") -> KEMRoundTrip:
    """Run a full ML-KEM keygen -> encapsulate -> decapsulate round trip.

    The sender and receiver should end up with the same 32-byte shared secret.
    """
    impl = _implementation(name)
    ek, dk = impl.keygen()  # type: ignore[attr-defined]
    shared_sender, ciphertext = impl.encaps(ek)  # type: ignore[attr-defined]
    shared_receiver = impl.decaps(dk, ciphertext)  # type: ignore[attr-defined]
    return KEMRoundTrip(
        parameter_set=PARAMETER_SETS[name],
        ek_len=len(ek),
        dk_len=len(dk),
        ct_len=len(ciphertext),
        shared_secret_sender=shared_sender,
        shared_secret_receiver=shared_receiver,
    )


def parameter_table() -> list[MLKEMParameterSet]:
    """Return the three standardised ML-KEM parameter sets."""
    return list(PARAMETER_SETS.values())
