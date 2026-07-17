"""Smoke tests for the staged CLI.

These assert the demonstrations run end to end and surface the key teaching
beats, without pinning every character of the Rich output (which would make the
tests brittle against cosmetic changes).
"""

from __future__ import annotations

from typer.testing import CliRunner

from qcrypto.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "qcrypto" in result.stdout


def test_rsa_demo_runs_all_five_steps() -> None:
    result = runner.invoke(app, ["rsa-demo"])
    assert result.exit_code == 0
    for step in range(1, 6):
        assert f"Step {step}/5" in result.stdout
    # The classical break must actually recover the factors of 21.
    assert "3" in result.stdout and "7" in result.stdout


def test_factor_command() -> None:
    result = runner.invoke(app, ["factor", "21"])
    assert result.exit_code == 0
    assert "3" in result.stdout
    assert "7" in result.stdout


def test_factor_rejects_bad_method() -> None:
    result = runner.invoke(app, ["factor", "21", "--method", "quantum"])
    assert result.exit_code != 0
