# Part 2 — Shor on Real IBM Quantum Hardware: The Honest Gap

> Part 1 factored 21 on a simulator, cleanly recovering the period from sharp
> interference peaks. This part takes the *exact same circuit* to a real IBM Quantum
> device and asks the question that separates hype from reality: does it still work?
> The answer — and *why* it is the answer — is the most important lesson in the series.

> **Status note.** This part is written to be run against your own IBM Quantum account
> (see [`docs/ibm-quantum-setup.md`](../ibm-quantum-setup.md)). The code path is complete;
> the measured histogram and its discussion should be filled in from *your* hardware run
> so the numbers are real rather than invented. Placeholders below are marked `‹…›`.

## The problem

A simulator computes the quantum state exactly. Real hardware does not: every gate has
an error rate, qubits decohere over time, and the device has a fixed connectivity graph
that forces extra SWAP gates when your circuit's interactions don't match its layout.
The question for Part 2 is whether a *genuine* Shor circuit — not one pre-simplified with
the answer — survives all of that on today's machines.

## Running it

With credentials saved, the same command that drove the simulator now targets hardware:

```
qcrypto shor-demo --backend ibm --ibm-backend ibm_kingston
```

Under the hood the circuit is transpiled onto the device's native basis gates and
coupling map at optimization level 3, submitted via the SamplerV2 primitive, and the
returned counts are post-processed with the identical continued-fraction pipeline from
Part 1. Nothing about the *algorithm* changes — only where it runs.

## Results

`‹Insert your measured histogram here — figures/10-shor-hardware-histogram.png — and the
top outcomes table.›`

Side by side with the simulator histogram from Part 1:

`‹Simulator: sharp peaks at 0, 341, 512, 683, 853 → clean r = 6.›`
`‹Hardware: broad, noisy distribution; peaks ‹present but degraded / washed out›; period
recovery ‹succeeded on N shots / failed›.›`

## Why the gap (this is the lesson)

Two forces degrade the hardware run:

1. **Depth after transpilation.** Our order-finding circuit uses multi-qubit
   controlled-multiplier gates. On a device with limited connectivity these decompose
   into long sequences of native two-qubit gates plus routing SWAPs. The transpiled depth
   is far larger than the tidy `~13` the simulator reported.

2. **Error accumulation.** With two-qubit gate error rates around 10⁻³ and a circuit
   containing many hundreds of them, the probability that *no* error corrupts a given shot
   is small. Errors smear amplitude away from the interference peaks, so the QFT readout
   is noisy.

There is no error correction here — these are noisy intermediate-scale quantum (NISQ)
devices. Shor's algorithm as written assumes *fault-tolerant* qubits, which do not yet
exist at the needed scale.

## The honest takeaway

This is the concrete, measured version of the point Part 0's exponential-wall chart made
abstractly. A genuine end-to-end Shor factorisation is out of reach on current hardware —
even for `N = 21` — and the distance to RSA-2048 (on the order of a million high-quality
logical qubits running for days, per Gidney 2025) is not incremental. When you see a
headline claiming a quantum computer "factored" a large number, check whether the circuit
was compiled using knowledge of the answer (Part 1's honesty section) or run on real
hardware at all. Almost always, one of those caveats applies.

None of this means the threat is fake. It means the threat is *future*, specific, and
quantifiable — which is exactly why the migration to post-quantum cryptography (Part 4)
is happening now, on a schedule set by *harvest-now, decrypt-later*, not by next year's
device.

---

### What's next

**Part 3 — Grover's Algorithm, and Why Your AES Keys Are Fine.** Having seen the limits of
even a working Shor circuit, we turn to the other famous quantum algorithm — and why its
merely *quadratic* speedup means symmetric cryptography needs only bigger keys, not
replacement.

---

*To reproduce: [`docs/ibm-quantum-setup.md`](../ibm-quantum-setup.md). Save the hardware
histogram as `figures/10-shor-hardware-histogram.png` and update the Results section with
your real numbers.*
