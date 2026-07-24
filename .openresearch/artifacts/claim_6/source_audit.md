# Claim 6 source audit

## Retrieval record

- Retrieval date: 2026-07-24.
- Browser User-Agent:
  `Mozilla/5.0 (compatible; OpenResearch-Reproduction/1.0; +https://github.com/MachineLearning-Nerd)`.
- Primary candidate URL:
  `https://ar5iv.labs.arxiv.org/html/2510.08419`.
- ar5iv HTML SHA-256:
  `21525cc7ffd769828c752aa1d03de4f38703163cb926c1053b16822bb9342bf5`.
- Version-pinned v1 PDF URL:
  `https://arxiv.org/pdf/2510.08419v1`.
- v1 PDF SHA-256:
  `88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7`.
- Version-pinned v2 PDF URL:
  `https://arxiv.org/pdf/2510.08419v2`.
- v2 PDF SHA-256:
  `9c66f6f41e25cfae267eb3edec0d61e252c563bceab210c289415e13592cb088`.

## Version decision

The supplied judge claim and section/equation anchors correspond to v1. The
ar5iv service returned the same older 26-page HTML bytes for the unversioned,
v1, and v2 HTML URLs, while arXiv's actual v2 PDF is a distinct 17-page
revision. This contract therefore pins v1 and states that choice explicitly.
The v2 paper retains the same D-RUT, RPE, Chebyshev, and Fourier reconstruction
components, but it is not silently substituted for the source judged here.

## Exact algorithm obligations

Algorithm 1 takes an unknown single-mode Hamiltonian, maximum order `d`, and
target precision `epsilon`. It specifies:

1. `d+1` radial Chebyshev nodes on a finite interval.
2. Angular samples `theta_(u,l) = pi*u/(l+1)`.
3. Displacement `beta = r_mu exp(i theta)`.
4. Vacuum plus ancilla preparation.
5. A controlled, Trotterized D-RUT sequence containing displacement and random
   number rotations.
6. X- and Y-basis ancilla measurements for robust phase estimation of
   `C(r_mu, theta)`.
7. Chebyshev/radial polynomial recovery.
8. Equation (30)'s inverse discrete Fourier transform to obtain every
   coefficient at each order.

Equation (24) gives the X-basis zero probability as
`(1 + cos(kappa C(beta)))/2`; Equation (25) gives the corresponding Y statistic
with `sin(kappa C(beta))`. Equations (26)-(30) factor the response into radial
polynomials and angular Fourier series.

## Assumptions and quantifiers

- Single bosonic mode.
- A finite maximum polynomial order `d`.
- Unitary access to the unknown Hamiltonian for the controlled D-RUT sequence.
- Vacuum-state and ancilla preparation.
- Implementable displacements and number rotations.
- An RPE branch range avoiding phase alias at the initial level.
- A finite radial interval whose design matrix has full column rank.

Claim 6 is a structural statement about the algorithmic composition rather than
a universal error or resource theorem. The verifier exercises each named stage
on one nontrivial Hermitian degree-2 Hamiltonian, checks the quantum response
against the independently evaluated polynomial constant, and reconstructs the
coefficients through the paper's factorized recovery formula.
