# Claim 1 method

The verifier instantiates the smallest genuinely multi-mode generic case:
two modes and total degree two. It includes all ten independent real
single-mode parameters and all four independent real two-mode pair/hopping
parameters.

The physical audit constructs an 11-by-11 Fock representation per mode,
forms the 121-dimensional Hamiltonian, applies a Kronecker product of two
matrix-exponential displacement operators, and performs the exact finite
13-by-13 independent cyclic phase average. It checks the vacuum constant
against the monomial formula and audits off-diagonal suppression.

For statistical scaling, every constant is estimated from binomial X/Y
ancilla outcomes at power-of-two RPE times. Each mode uses the paper's
Chebyshev/IDFT design; eight two-mode points recover coupling residuals after
hierarchical single-mode subtraction. Seven fixed horizons and 24 independent
replicates are run.

The same total evolution budget is assigned to a physical Ramsey control that
uses only `kappa=1` and estimates phase from sampled X/Y outcomes. This tests
the standard-quantum-limit alternative without injecting `1/sqrt(T)` noise.

The proof certificate independently records
`T_J=2 S sum_(j=0)^J 2^j=2S(2^(J+1)-1)`. For fixed finite `N,d`, the design
point count and inverse-design norm do not depend on `epsilon`; therefore an
RPE error proportional to `2^-J` implies total coefficient RMSE
`O(1/T_J)`.
