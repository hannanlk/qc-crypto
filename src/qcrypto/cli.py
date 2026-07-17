"""Staged, educational command-line interface.

Design goal (per project brief): *not* a cluttered CLI that dumps filler output.
Each command walks through an algorithm one clearly delimited step at a time —
one panel per conceptual stage, the key numbers surfaced, and a short "why this
matters" note. The heavy logic lives in :mod:`qcrypto.classical`; the CLI only
orchestrates and presents, so the terminal view and the notebooks share exactly
the same underlying implementation.

Phase 0 exposes two commands:

* ``qcrypto rsa-demo`` — build a toy RSA key, encrypt/decrypt, then break it
  classically by factoring the modulus and reconstructing the private key.
* ``qcrypto factor``   — factor an integer with a chosen classical method and
  report timing (the baseline Shor will later be compared against).
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from qcrypto import __version__
from qcrypto.classical.factoring import factor
from qcrypto.classical.rsa import encrypt, keypair_from_primes, recover_private_exponent

app = typer.Typer(
    add_completion=False,
    help="qcrypto — an honest, hands-on tour of quantum computing vs. cryptography.",
)
console = Console()

# A muted, consistent visual language for the staged output.
_ACCENT = "cyan"
_OK = "green"
_WARN = "yellow"
_DANGER = "red"


def _step(index: int, total: int, title: str, body: Text | Table, style: str = _ACCENT) -> None:
    """Render one stage of a demonstration as a titled panel."""
    console.print(
        Panel(
            body,
            title=f"[bold]Step {index}/{total} — {title}[/bold]",
            border_style=style,
            padding=(1, 2),
        )
    )


@app.command()
def version() -> None:
    """Print the qcrypto version."""
    console.print(f"qcrypto {__version__}")


@app.command("rsa-demo")
def rsa_demo(
    p: Annotated[int, typer.Option(help="First secret prime.")] = 3,
    q: Annotated[int, typer.Option(help="Second secret prime.")] = 7,
    message: Annotated[int, typer.Option(help="Integer message to encrypt (0 <= m < n).")] = 4,
    e: Annotated[int | None, typer.Option(help="Public exponent; auto-chosen if omitted.")] = None,
) -> None:
    """Walk through RSA end to end on a toy modulus, then break it classically.

    The default (p=3, q=7 -> n=21) is the project's canonical toy modulus.
    """
    total = 5
    kp = keypair_from_primes(p, q, e)

    # Step 1 — the setup.
    setup = Text()
    setup.append("Two secret primes are chosen and multiplied.\n\n", style="dim")
    setup.append(f"  p = {kp.p}\n  q = {kp.q}\n")
    setup.append(f"  n = p x q = {kp.n}", style=f"bold {_ACCENT}")
    setup.append("\n\nThe modulus n is public; p and q are the secret an attacker wants.")
    _step(1, total, "Setup: choose the primes", setup)

    # Step 2 — key generation.
    keygen = Table.grid(padding=(0, 2))
    keygen.add_column(justify="right", style="dim")
    keygen.add_column(style="bold")
    keygen.add_row("phi(n) = (p-1)(q-1)", str(kp.phi))
    keygen.add_row("public exponent e", str(kp.e))
    keygen.add_row("private exponent d = e^-1 mod phi(n)", str(kp.d))
    keygen.add_row("public key (n, e)", str(kp.public_key))
    keygen.add_row("private key (n, d)", str(kp.private_key))
    _step(2, total, "Key generation", keygen)
    if kp.exponents_coincide:
        console.print(
            f"  [{_WARN}]Note:[/{_WARN}] e == d here. This is a small-modulus artifact "
            f"(phi={kp.phi} has group exponent 2), [bold]not[/bold] a real-world RSA "
            "property. Real keys have e != d.\n"
        )

    # Step 3 — encryption.
    ciphertext = encrypt(message, kp.public_key)
    enc = Text()
    enc.append("Encryption uses only the public key:\n\n", style="dim")
    enc.append(f"  c = m^e mod n = {message}^{kp.e} mod {kp.n} = ", style="")
    enc.append(str(ciphertext), style=f"bold {_ACCENT}")
    _step(3, total, "Encrypt the message", enc)

    # Step 4 — legitimate decryption.
    recovered = pow(ciphertext, kp.d, kp.n)
    dec = Text()
    dec.append("The key holder decrypts with the private exponent:\n\n", style="dim")
    dec.append(f"  m = c^d mod n = {ciphertext}^{kp.d} mod {kp.n} = ")
    dec.append(str(recovered), style=f"bold {_OK}")
    dec.append("\n\n")
    if recovered == message:
        dec.append("Round-trip verified: decrypted text matches the original.", style=_OK)
    else:
        dec.append("Round-trip FAILED — this should never happen.", style=_DANGER)
    _step(4, total, "Legitimate decryption", dec, style=_OK)

    # Step 5 — the classical break.
    result = factor(kp.n, method="auto")
    fp, fq = result.factors
    d_attacker = recover_private_exponent(kp.n, kp.e, fp, fq)
    attacker_plaintext = pow(ciphertext, d_attacker, kp.n)

    break_body = Text()
    break_body.append("An attacker sees only (n, e) and the ciphertext c.\n", style="dim")
    break_body.append("The moment they factor n, the private key falls out:\n\n", style="dim")
    break_body.append(f"  factor(n={kp.n}) -> ({fp}, {fq})   ", style=f"bold {_DANGER}")
    break_body.append(f"[{result.method}, {result.elapsed_seconds * 1e6:.1f} us]\n", style="dim")
    break_body.append(f"  recovered d = {d_attacker}\n", style=f"bold {_DANGER}")
    break_body.append(f"  decrypted c -> {attacker_plaintext}", style=f"bold {_DANGER}")
    break_body.append("\n\n")
    break_body.append(
        "This is the entire thesis: RSA's security IS the hardness of factoring n. "
        "Shor's algorithm (Phase 1) attacks precisely this step — it factors n in "
        "polynomial time on a fault-tolerant machine. Everything after factoring is "
        "the same elementary arithmetic you just saw.",
        style="italic",
    )
    _step(5, total, "The classical break: factor n, recover d", break_body, style=_DANGER)


@app.command(name="factor")
def factor_cmd(
    n: Annotated[int, typer.Argument(help="Integer to factor (a semiprime for a clean result).")],
    method: Annotated[
        str,
        typer.Option(help="trial_division | fermat | pollard_rho | auto"),
    ] = "auto",
) -> None:
    """Factor an integer classically and report the method and timing."""
    result = factor(n, method=method)
    table = Table(title=f"Factorisation of {n}", border_style=_ACCENT)
    table.add_column("Field", style="dim")
    table.add_column("Value", style="bold")
    table.add_row("factors", " x ".join(str(f) for f in result.factors))
    table.add_row("method", result.method)
    table.add_row("iterations", str(result.iterations))
    table.add_row("elapsed", f"{result.elapsed_seconds * 1e6:.1f} us")
    table.add_row("verified", "yes" if result.verify() else "NO")
    console.print(table)


def main() -> None:
    """Console-script entry point."""
    app()


if __name__ == "__main__":
    main()
