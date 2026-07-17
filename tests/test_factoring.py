"""Tests for the classical factoring baselines."""

from __future__ import annotations

import pytest

from qcrypto.classical.factoring import factor, fermat, pollard_rho, trial_division


def test_trial_division_factors_21() -> None:
    result = trial_division(21)
    assert result.factors == (3, 7)
    assert result.verify()
    assert result.method == "trial_division"


def test_trial_division_on_prime_raises() -> None:
    with pytest.raises(ValueError):
        trial_division(13)


def test_fermat_factors_21() -> None:
    result = fermat(21)
    assert result.factors == (3, 7)
    assert result.verify()


def test_fermat_rejects_even() -> None:
    with pytest.raises(ValueError):
        fermat(20)


def test_pollard_rho_factors_21_with_working_constant() -> None:
    # c = 1 hits the trivial-factor failure mode for n = 21; c = 2 succeeds.
    result = pollard_rho(21, c=2)
    assert result.factors == (3, 7)
    assert result.verify()


def test_pollard_rho_rejects_even() -> None:
    with pytest.raises(ValueError):
        pollard_rho(20)


@pytest.mark.parametrize(
    ("n", "expected"),
    [(15, (3, 5)), (21, (3, 7)), (35, (5, 7)), (77, (7, 11)), (8051, (83, 97))],
)
def test_auto_factors_semiprimes(n: int, expected: tuple[int, int]) -> None:
    result = factor(n, method="auto")
    assert result.factors == expected
    assert result.verify()


def test_auto_handles_even_semiprime() -> None:
    result = factor(22, method="auto")
    assert result.factors == (2, 11)
    assert result.verify()


def test_factor_rejects_unknown_method() -> None:
    with pytest.raises(ValueError):
        factor(21, method="quantum")  # not a Phase 0 method


def test_factor_rejects_tiny_input() -> None:
    with pytest.raises(ValueError):
        factor(3)
