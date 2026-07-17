"""Tests for the Grover-vs-AES security framing (no quantum backend needed)."""

from __future__ import annotations

from qcrypto.analysis.symmetric_security import grover_security_table


def test_grover_bits_are_half_the_key() -> None:
    for cipher in grover_security_table():
        assert cipher.grover_bits == cipher.key_bits // 2


def test_expected_family() -> None:
    table = {c.name: c for c in grover_security_table()}
    assert set(table) == {"AES-128", "AES-192", "AES-256"}
    assert table["AES-128"].grover_bits == 64
    assert table["AES-256"].grover_bits == 128
    assert table["AES-256"].nist_pq_category == 5
