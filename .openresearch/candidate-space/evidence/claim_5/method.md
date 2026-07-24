# Claim 5 method

SymPy first certifies the exact Bogoliubov signal
`g'20=(omega/2)sinh(2 Delta R)`, its known zero, and nonzero derivative. The
reference mismatch is checked against the paper's printed RPE-overlap
condition.

Each outer-loop query builds the mismatched Hamiltonian in a 24-state Fock
representation. At three Chebyshev radii and angles zero and `pi/2`, the code
applies physical displacement and a 29-phase number twirl. Sampled X/Y ancilla
statistics feed the same power-of-two robust phase estimator used by Claim 6.
The angular contrast
`C(r,0)-C(r,pi/2)=4 r^2 g'20` recovers the signal used for the bisection sign.

To avoid choosing the inner resource from the formula under test, the code
sweeps five predeclared RPE horizons on a disjoint `|Delta R|=2e-4` sign task.
The first horizon whose 95% Wilson lower bound reaches 0.90 is frozen for
validation. The lowest horizon is a predeclared underpowered control.

Thirty-two new bisections are then run at each of five precision targets.
Every target must achieve a 95% Wilson lower success bound of at least 0.85.
The exact proof certificate independently checks that a valid bracket has
width `W/2^n` and midpoint error at most `W/2^(n+1)`, yielding
`n=ceil(log2(W/(2 epsilon_R)))`.

The barren-plateau control sets the response coefficient to zero, so a sign
bracket cannot be formed. The historical `x^2` proxy is also audited: on the
tested interval it has no sign-changing bracket and therefore does not
instantiate the paper's algorithm.
