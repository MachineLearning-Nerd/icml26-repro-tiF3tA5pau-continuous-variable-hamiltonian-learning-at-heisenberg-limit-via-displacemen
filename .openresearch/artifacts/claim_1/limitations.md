# Claim 1 limitations and deviations

- The executable physical instance is the complete two-mode, degree-two
  Hermitian family. The algebraic certificate covers fixed finite mode count
  and degree; no favorable scaling in growing mode count or degree is claimed.
- The finite cyclic twirl is exact because its phase count exceeds the Fock
  cutoff. Hardware would approximate the continuous average stochastically.
- The physical matrix audit uses cutoff 11. Agreement with the analytic
  constant is required, but this is not an infinite-dimensional error bound.
- The ideal effective evolution is sampled directly from the paper's ancilla
  probabilities. Gate synthesis and finite-Trotter error are not simulated;
  the theorem itself assumes `L` is large enough to place that error within
  RPE tolerance.
- The result verifies an upper-bound scaling for the named protocol. It does
  not establish an information-theoretic lower bound over every possible
  Hamiltonian-learning protocol.
