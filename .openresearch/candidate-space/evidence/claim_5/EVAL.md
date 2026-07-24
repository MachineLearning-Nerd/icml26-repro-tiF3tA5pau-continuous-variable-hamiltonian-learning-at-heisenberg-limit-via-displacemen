# Claim 5 evaluation

Status: `VERIFIED` for the exact conditional bisection theorem in Section 5.3.

Formal OpenResearch run `a18c9a9f-82fc-41a0-bc03-27786fc277f8` executed commit
`72518d15b683b450274406736e0bbe3488c09800` with the fixed cumulative command.
The run ended successfully in 30 seconds on local CPU with a one-thread cap.

The result is proof-led. SymPy certifies the physical Bogoliubov signal
`g'20=(omega/2)sinh(2 Delta R)`, its known zero, and nonzero derivative.
The exact interval certificate proves the bracket width and midpoint-error
bounds for every iteration. An independently calibrated finite-Fock
D-RUT/RPE oracle supplies the signs in 160 disjoint validation bisections.

All five precision levels passed 32/32 trials (Wilson 95% lower bound
`0.892817`), with iteration counts `[2,3,4,5,6]` and log2-inverse-precision
slope `1.0`. The first calibrated RPE horizon was level 10; the predeclared
level-8 underpowered control failed calibration. The barren signal and
historical `x^2` proxy both lacked a valid sign bracket.

The independent checker passed. A tampered exact-identity acceptance field
made it exit with status one. The verdict is scoped to the paper's explicit
valid-bracket, non-barren-response, overlap, and sign-oracle assumptions; it
does not establish Theorem 2's total evolution-time scaling.
