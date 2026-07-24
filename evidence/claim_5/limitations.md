# Claim 5 limitations and deviations

- The theorem's logarithmic iteration count is conditional on a valid bracket
  and reliable signs. Both conditions are explicit in the contract.
- The exact interval-contraction proof establishes the asymptotic iteration
  claim. Finite noisy trials validate the implemented D-RUT/RPE oracle but are
  not extrapolated into a universal theorem.
- The selected inner RPE horizon comes from an independent predeclared
  calibration sweep. This claim does not by itself establish the total
  evolution-time scaling in Theorem 2; that is assessed under Claim 2.
- The physical instance is the number Hamiltonian
  `H=omega B^dagger B`. It is deliberately chosen because the paper's stated
  `g'20` known-zero signal is exact and analytically auditable.
- Finite-Fock cutoff 24 and the 29-phase cyclic twirl are simulation choices.
  Agreement with the analytic Bogoliubov response is required.
- The validation success criterion is probabilistic and reported with Wilson
  confidence intervals. It is not a claim of zero sign-error probability.
