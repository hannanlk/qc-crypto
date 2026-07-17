"""Tests for the textbook RSA implementation, centred on the N = 21 toy."""

from __future__ import annotations

import pytest

from qcrypto.classical.rsa import (
    RSAKeyPair,
    decrypt,
    encrypt,
    generate_keypair,
    keypair_from_primes,
    recover_private_exponent,
)


def test_toy_modulus_21_structure() -> None:
    kp = keypair_from_primes(3, 7)
    assert kp.n == 21
    assert kp.phi == 12
    assert kp.e == 5  # smallest exponent coprime to 12
    assert kp.d == 5  # 5 is its own inverse mod 12


def test_e_equals_d_is_flagged_for_n21() -> None:
    """The e == d artifact must be detectable, not silently misleading."""
    kp = keypair_from_primes(3, 7)
    assert kp.exponents_coincide is True


def test_roundtrip_all_messages_mod_21() -> None:
    kp = keypair_from_primes(3, 7)
    for m in range(kp.n):
        c = encrypt(m, kp.public_key)
        assert decrypt(c, kp.private_key) == m


def test_encrypt_rejects_out_of_range_message() -> None:
    kp = keypair_from_primes(3, 7)
    with pytest.raises(ValueError):
        encrypt(kp.n, kp.public_key)  # m must be < n


def test_keypair_rejects_non_prime_and_equal_primes() -> None:
    with pytest.raises(ValueError):
        keypair_from_primes(4, 7)  # 4 is not prime
    with pytest.raises(ValueError):
        keypair_from_primes(7, 7)  # not distinct


def test_recover_private_exponent_matches_real_d() -> None:
    kp = keypair_from_primes(3, 7)
    d_attacker = recover_private_exponent(kp.n, kp.e, kp.p, kp.q)
    assert d_attacker == kp.d


def test_recover_private_exponent_rejects_wrong_factors() -> None:
    with pytest.raises(ValueError):
        recover_private_exponent(21, 5, 3, 5)  # 3 * 5 != 21


@pytest.mark.parametrize("bits", [32, 64])
def test_generated_key_roundtrips_and_has_distinct_exponents(bits: int) -> None:
    kp = generate_keypair(bits)
    assert kp.n.bit_length() in (bits - 1, bits)
    assert kp.e != kp.d  # realistic keys do not have e == d
    message = 123456 % kp.n
    assert decrypt(encrypt(message, kp.public_key), kp.private_key) == message


def test_keypair_is_immutable() -> None:
    kp = keypair_from_primes(3, 7)
    with pytest.raises(Exception):  # noqa: B017 - frozen dataclass raises FrozenInstanceError
        kp.e = 11  # type: ignore[misc]
    assert isinstance(kp, RSAKeyPair)
