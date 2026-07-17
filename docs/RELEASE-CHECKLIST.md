# Public Release Checklist

Run through this before flipping the repository to public and publishing the article.

## Code quality

- [ ] `python -m ruff format --check .` clean
- [ ] `python -m ruff check .` clean
- [ ] `python -m mypy` clean
- [ ] `python -m pytest` green with `[dev,quantum,pqc]` installed (incl. slow sim tests)
- [ ] CI passing on the `main` branch (classical suite, Python 3.10–3.12)

## Figures

- [ ] `python scripts/make_wall_chart.py` regenerates figure 03
- [ ] `python scripts/make_shor_figures.py` regenerates figures 04–05
- [ ] `python scripts/make_grover_figures.py` regenerates figures 07–08
- [ ] All committed SVGs render with a white background

## Phase 2 (hardware) — when the IBM account exists

- [ ] Credentials saved (`docs/ibm-quantum-setup.md`), token **not** committed
- [ ] `qcrypto shor-demo --backend ibm` run once; histogram saved as
      `figures/10-shor-hardware-histogram.png`
- [ ] Part 2 article Results section filled in with the real numbers (remove `‹…›`
      placeholders)

## Security / hygiene

- [ ] No secrets committed (grep for tokens; confirm `.gitignore` covers `.env`,
      `*.token`, `.qiskit/`)
- [ ] `git log` history contains no credentials
- [ ] LICENSE present (MIT); third-party licenses acknowledged (`kyber-py`: MIT/Apache-2.0)

## Article & narrative

- [ ] All five parts read end-to-end; cross-links work
- [ ] "runs today vs. fault-tolerant future" distinction explicit in each part
- [ ] Honesty sections present: compiled-vs-genuine Shor (Part 1), hardware gap (Part 2),
      "no known attack" vs "proven secure" (Part 4)

## Publication

- [ ] README badges/links point at the correct repo URL
- [ ] (Optional) Mint a Zenodo DOI for citability
- [ ] LinkedIn posts (`docs/linkedin-posts.md`) queued with real links
- [ ] Repo set to public
