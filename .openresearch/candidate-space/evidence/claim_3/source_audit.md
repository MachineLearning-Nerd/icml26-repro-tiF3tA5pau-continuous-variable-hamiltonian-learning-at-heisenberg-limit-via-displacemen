# Claim 3 source audit

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

The supplied judge anchors correspond to v1, so the contract pins v1 rather
than silently substituting v2.

## Exact statement, assumptions, and quantifiers

Section 3.6 models the actual displacement at measurement point `j` as
`beta_tilde_j=beta_j+delta beta_j`. Equations (36)-(40) separate the resulting
coefficient error from RPE statistical noise:

`delta g_SPAM = K^+[C(beta_tilde)-C(beta)]`.

Equation (41) applies the pseudoinverse operator norm, Equation (42) assumes a
Lipschitz bound for the response vector, and Equation (43) concludes

`||delta g_SPAM||_2 <= L_C/sigma_min(K) ||delta beta||_2`.

The operative assumptions are:

- `K` is the well-defined combined recovery design and has a nonzero smallest
  singular value.
- Nominal and perturbed displacements stay in a domain on which one common
  Lipschitz constant holds.
- `delta g_SPAM` includes displacement miscalibration only; RPE statistical
  error is the separate term in Equation (40).

Section 3.6.1 defines `L_C=sup ||grad C(r,theta)||_2` and bounds radial and
angular derivatives in Equations (44)-(46). For a vector of independently
perturbed measurement points, the response Jacobian is block diagonal, so its
operator norm is the maximum scalar-response gradient norm.

## Exact degree-2 response

For Hermitian coefficients parameterized by
`[a,b,c,d,e]=[Re(g10),Im(g10),Re(g20),Im(g20),g11]` and
`beta=x+i y`, the D-RUT constant is

`C(x,y)=2ax+2by+2c(x^2-y^2)+4dxy+e(x^2+y^2)`.

Its gradient is affine, `grad C=h+H[x,y]`. On the disk `|beta|<=R`,
the triangle and spectral-norm inequalities give the certified global
constant `L_C=||h||_2+||H||_2 R`. This is calculated from the physical
coefficients; it is not assigned an arbitrary value.
