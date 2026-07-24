# Claim 6 method

The experiment constructs creation and annihilation matrices in a 24-level Fock
truncation and a Hermitian normal-ordered degree-2 Hamiltonian with five nonzero
real/complex coefficients. For each Algorithm 1 displacement:

1. A matrix exponential forms the physical displacement operator.
2. The displaced Hamiltonian is averaged over seven equally spaced number
   rotations. Seven phases exactly remove all number changes possible at degree
   two; the remaining finite-cutoff error is measured rather than assumed.
3. The vacuum eigenvalue of the twirled Hamiltonian determines the ancilla X/Y
   probabilities.
4. Binomial samples with seed `251008419` feed an iterative power-of-two phase
   unwrap through `kappa=4096`.
5. Three mapped Chebyshev nodes recover the radial coefficients for every
   required angle.
6. Equation (30), implemented literally, recovers the Hamiltonian coefficients.

An independent checker ignores the radial/DFT factorization and solves a single
full complex design matrix from the same RPE responses. Agreement between the
two routes is required.

The displacement-omission control forces every response to zero and must miss
the nonzero coefficients. The twirl-omission control evolves the displaced
Hamiltonian directly and must show vacuum leakage, invalidating RPE's scalar
eigenphase response model for the intended physical reason.

The RMSE threshold was fixed before execution at `2.5e-3`. It is substantially
larger than the final-level phase standard error propagated through the measured
design condition, but far below both negative-control error and the smallest
nonzero coefficient magnitude.
