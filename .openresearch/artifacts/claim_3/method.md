# Claim 3 method

The accepted Claim 6 Hamiltonian and Algorithm 1 sampling design are reused:
three Chebyshev radii, four required angular values, a 24-state Fock
representation, physical displacement matrices, and an exact 29-phase
number-rotation twirl.

The combined real design matrix maps the five independent Hermitian
coefficients directly to the twelve D-RUT constants. Its smallest singular
value and pseudoinverse norm are measured independently. SymPy differentiates
the physical response polynomial exactly. A global Lipschitz constant is then
certified on `|beta|<=0.70` from the affine gradient, rather than setting
`L_C=1`.

The universal certificate is the composition

1. the mean-value inequality for each D-RUT response,
2. the block-diagonal response Jacobian bound
   `||delta C||<=L_C||delta beta||`, and
3. `||K^+||_2=1/sigma_min(K)`.

Finite-Fock evidence checks that the response used in this derivation is the
one produced by physical displacement plus number twirling. Twelve seeded
directions are generated once, and each is evaluated at the same five
predeclared magnitudes, giving sixty paired perturbations. This pairing avoids
confounding scale with direction-dependent amplification. A log-log slope is
measured only as corroboration of the small-error behavior; the universal
upper bound is established algebraically rather than inferred from this
sweep.

The negative control computes an adversarial local perturbation direction and
replaces the derived `L_C` by `L_C/1000`. The bound must fail, demonstrating
why an arbitrary constant such as the historical baseline's `L_C=1` is not
accepted.
