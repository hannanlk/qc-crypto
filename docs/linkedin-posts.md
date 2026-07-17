# LinkedIn Posts

Drafts to accompany the series. Tone: technical, honest, no hype. Adjust links and
hashtags before posting. Each is designed to stand alone.

---

## Post 1 — Series launch

I keep seeing "quantum computers will break all encryption." It's wrong — and the real
story is more interesting.

So I built it, in runnable code: factor a toy RSA key with Shor's algorithm (simulator
*and* real IBM Quantum hardware), show why Grover barely dents AES, and end at ML-KEM,
the NIST replacement for RSA.

The theme throughout: correctness over hype. Every quantum result is checked against a
classical baseline, and the line between "runs today" and "needs a fault-tolerant
machine that doesn't exist yet" is drawn explicitly.

Part 0 is up 👇 [link]

#QuantumComputing #Cryptography #Cybersecurity #Qiskit

---

## Post 2 — Shor / RSA

Everyone says "Shor's algorithm breaks RSA." Almost no one shows what that actually
means.

RSA's security is exactly one thing: the difficulty of factoring a large number. Shor
turns factoring into *period-finding* — something a quantum computer does with
interference and a Quantum Fourier Transform.

In Part 1, I factor N = 21 on a simulator: the circuit finds the period r = 6, and out
pop the factors 3 and 7. No hardcoded answers — genuine period-finding. (The infamous
"factored 15!" demos often bake in the answer. I explain how to spot that.)

The catch is in Part 2. 👇 [link]

#QuantumComputing #Cryptography #Qiskit

---

## Post 3 — Hardware reality

I ran a genuine Shor circuit on real IBM Quantum hardware. It struggled to factor 21.

That's not a failure — it's the most honest result in the whole project.

On a simulator: sharp interference peaks, clean period, instant factors. On a real
device: gate errors (~10⁻³ each) and decoherence smear those peaks into noise. There's
no error correction — these are NISQ machines, and Shor assumes fault-tolerant qubits
that don't exist at scale yet.

The distance from "factor 21 on hardware" to "break RSA-2048" (est. ~1M high-quality
qubits for days) is not incremental. That gap is why your RSA keys are safe *today* —
and why "harvest now, decrypt later" still means you should care. [link]

#QuantumComputing #Cybersecurity #NISQ

---

## Post 4 — Grover / AES

"If quantum breaks RSA, surely it breaks AES too?" No — and the reason is one of the
cleanest ideas in the field.

Breaking a symmetric key is unstructured search. The best quantum algorithm for that is
Grover's — and it's only a *quadratic* speedup: 2^k → 2^(k/2). It halves the exponent,
it doesn't collapse it. AES-256 under Grover still needs ~2^128 work.

And Grover barely parallelizes, so real attacks cost even more. NIST still rates AES-128
as post-quantum Category 1. The fix for symmetric crypto is trivial: use 256-bit keys.

Exponential Shor vs. quadratic Grover — that asymmetry is the whole story. [link]

#QuantumComputing #Cryptography #AES

---

## Post 5 — ML-KEM / finale

RSA and ECC can't be saved by bigger keys — Shor is exponential. They have to be
replaced. Here's the replacement.

Part 4 covers ML-KEM (FIPS 203, formerly Kyber): NIST's lattice-based key-encapsulation
standard. Its security rests on a lattice problem with no known efficient quantum
attack — and I'm careful to say "no known attack," not "proven secure," because those
are different things.

It's already deployed in hybrid mode (X25519 + ML-KEM) in major browsers. The
post-quantum migration isn't hypothetical; it's shipping.

Full series, all code open-source 👇 [link]

#QuantumComputing #PostQuantumCryptography #Cybersecurity #MLKEM
