# Claim 5 source audit

## Retrieval and version

- Retrieval date: 2026-07-24.
- Browser User-Agent:
  `Mozilla/5.0 (compatible; OpenResearch-Reproduction/1.0; +https://github.com/MachineLearning-Nerd)`.
- ar5iv URL: `https://ar5iv.labs.arxiv.org/html/2510.08419`.
- ar5iv HTML SHA-256:
  `21525cc7ffd769828c752aa1d03de4f38703163cb926c1053b16822bb9342bf5`.
- Version-pinned v1 PDF: `https://arxiv.org/pdf/2510.08419v1`.
- v1 PDF SHA-256:
  `88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7`.
- v2 PDF SHA-256:
  `9c66f6f41e25cfae267eb3edec0d61e252c563bceab210c289415e13592cb088`.

The judge's Section 5.3 and Equation (77)-(78) anchors refer to v1.

## Exact statement and assumptions

Equation (71) relates the physical and reference bosonic bases by
`B=B'cosh(Delta R)+B'^dagger sinh(Delta R)`. The paper assumes prior knowledge
of at least one coefficient that is zero in the physical basis. Basis mismatch
makes that coefficient a signal `f(Delta R)`.

Equations (72)-(76) derive its Bogoliubov dependence. Equation (77) writes the
observed signal as `K Delta R` plus D-RUT statistical noise and higher-order
terms. Equation (78) requires the signal magnitude to resolve the inner-loop
noise. The following prose says the search needs
`O(log(1/epsilon_R))` iterations. It explicitly identifies a signal that
vanishes in a neighborhood—every derivative zero—as a barren plateau.

Section 6.1 adds:

- the reference frame must satisfy the printed RPE-overlap inequality;
- the initial interval must obey that condition and contain the solution;
- each bisection query runs the D-RUT inner loop; and
- `g'20(Delta R)` is a concrete signal choice.

Thus logarithmic contraction is conditional on a valid bracket, a
sign-informative signal, and an inner oracle precise enough to identify its
sign. Those conditions are part of this contract, not hidden implementation
details.

## Concrete exact signal

For `H=omega B^dagger B`, substitution of Equation (71) and normal ordering
gives

`g'20(Delta R)=omega sinh(Delta R)cosh(Delta R)`
`=(omega/2)sinh(2 Delta R)`.

It is exactly zero at `Delta R=0`, has derivative `omega` there, and is
strictly monotone. It therefore instantiates the paper's known-zero,
nonvanishing-response assumption without replacing the signal by an unrelated
root-finding function.
