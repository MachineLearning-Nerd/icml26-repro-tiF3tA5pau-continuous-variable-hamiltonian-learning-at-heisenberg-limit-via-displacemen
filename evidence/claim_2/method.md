# Claim 2 method

The physical instance is an unknown harmonic oscillator in a known reference
frame. Its exact mismatch signal is
`g20=(omega/2)sinh(2 DeltaR)` and `g11=omega cosh(2 DeltaR)`.
Each bisection query obtains both from two displaced D-RUT constants at angles
zero and pi/2 using sampled power-of-two RPE.

For five physical RMSE targets, eight predeclared RPE horizons are calibrated
on 16 seeds. The first empirical success is frozen and run on 32 disjoint
seeds. The exact total evolution time includes every outer query and final
measurement.

SymPy independently constructs the full quadratic map from
`[Re(g20),Im(g20),g11]` to `[G20,G11,G02]` and certifies determinant two.
This demonstrates recovery of physical rather than merely bosonic
coefficients.
