# Claim 4 source audit

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

The supplied judge claim and equation anchors correspond to v1. The ar5iv
service returned the same older 26-page HTML bytes for the unversioned, v1, and
v2 HTML URLs, while the actual arXiv v2 PDF differs. This contract therefore
pins v1.

## Exact statement and quantifiers

Section 4.1 describes two stages: learn single-mode coefficients with only the
target mode displaced, then subtract the learned single-mode response and
recover coupling coefficients. The main-results text writes
`Cov(delta g)_hierarchical <= Cov(delta g)_simultaneous` in Loewner order and
says this yields lower or equal variance “for all parameters.”

Appendix A defines the simultaneous design as `[M1 M2]` in Equation (92), with
`A=M1^dagger M1`, `B=M1^dagger M2`, and `D=M2^dagger M2`. Equations (93)-(95)
give the simultaneous block covariances and the hierarchical single-mode
covariance. Equations (96)-(105) explicitly assume that the two hierarchical
D-RUT datasets are independent and have common isotropic variance
`epsilon_C^2 I`. Equations (106) and (108) prove domination of the two diagonal
parameter blocks.

The inverses used in Equations (93)-(108) require `A`, `D`, and the joint Gram
matrix to be nonsingular. Although the prose calls the diagonal blocks
positive semidefinite, ordinary inverses make positive definiteness/full column
rank the operative assumption.

## Reconstructed full-covariance obligation

The appendix does not print the hierarchical cross-covariance, even though the
second-stage estimate inherits the first-stage error. To test the headline
matrix inequality rather than only two marginal inequalities, this verifier
includes that cross-covariance. For every full-rank design satisfying the
paper's noise assumptions it derives

`Cov_sim - Cov_hier = Z Q^{-1} Z^dagger`,

where `Q=D-B^dagger A^{-1}B` and
`Z=[A^{-1}B; -D^{-1}B^dagger A^{-1}B]`. Since `Q` is the positive-definite
Schur complement of the joint Gram matrix, this is a universal
positive-semidefinite certificate.
