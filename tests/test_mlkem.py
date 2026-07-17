"""Tests for the ML-KEM wrapper (require the pqc extra; auto-skipped otherwise)."""

from __future__ import annotations

import pytest

pytest.importorskip("kyber_py")

from qcrypto.pqc.mlkem import PARAMETER_SETS, parameter_table, run_roundtrip  # noqa: E402


@pytest.mark.parametrize("name", ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"])
def test_roundtrip_agrees_and_sizes_match(name: str) -> None:
    result = run_roundtrip(name)
    assert result.agreed
    assert len(result.shared_secret_sender) == 32
    assert result.sizes_match_standard


def test_shared_secret_is_random_per_run() -> None:
    a = run_roundtrip("ML-KEM-512")
    b = run_roundtrip("ML-KEM-512")
    # Independent encapsulations should (overwhelmingly) yield different secrets.
    assert a.shared_secret_sender != b.shared_secret_sender


def test_unknown_parameter_set_raises() -> None:
    with pytest.raises(ValueError):
        run_roundtrip("ML-KEM-2048")


def test_parameter_table_is_complete() -> None:
    names = {p.name for p in parameter_table()}
    assert names == set(PARAMETER_SETS)
    assert {p.nist_level for p in parameter_table()} == {1, 3, 5}
