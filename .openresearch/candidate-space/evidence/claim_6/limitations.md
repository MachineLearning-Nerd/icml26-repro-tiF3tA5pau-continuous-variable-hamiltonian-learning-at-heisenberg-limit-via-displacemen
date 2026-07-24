# Claim 6 limitations and deviations

- The bosonic Hilbert space is truncated at 24 Fock states. The resulting
  displacement error is explicitly compared with the infinite-dimensional
  polynomial response and must remain below the predeclared threshold.
- The continuous random-unitary expectation is replaced by a 29-point discrete
  phase twirl. Since 29 exceeds every possible nonzero index difference in the
  24-state truncated matrix, the cyclic average is the exact U(1) projection on
  this finite representation; residual off-diagonal norm is still measured.
- Ancilla measurements are sampled from the exact quantum probabilities rather
  than executed on physical hardware.
- The D-RUT effective Hamiltonian is formed directly by the finite twirl rather
  than by a finite-`L` product-formula approximation. This isolates Claim 6's
  named reconstruction pipeline and does not test Trotter-error scaling.
- The experiment verifies the algorithmic composition on one deterministic
  nontrivial instance. It is not evidence for Claims 1 or 2's universal
  complexity statements.
