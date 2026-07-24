# Claim 3 limitations and deviations

- The paper labels displacement miscalibration as SPAM. The contract tests
  exactly that model, not every possible state-preparation or measurement
  channel.
- RPE statistical noise is excluded because Equation (40) defines it as a
  separate additive error term.
- The finite-Fock simulation uses cutoff 24 and an exact finite cyclic twirl.
  Agreement with the analytic D-RUT polynomial is explicitly required.
- The concrete perturbation sweep is not proof of the universal inequality.
  Universal scope comes from the symbolic response gradient, global
  Lipschitz certificate, and operator-norm derivation.
- The Lipschitz value is a certified upper bound, not claimed to be the
  smallest possible constant. It is nevertheless derived from the actual
  coefficients and checked with a nonvacuous failure control.
- The contract covers perturbations that remain within `|beta|<=0.70`.
  Equation (43) requires some bounded domain for finite `L_C`; it is not a
  global claim over unbounded displacement.
