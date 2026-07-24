# Claim 1 evaluation

Status: `VERIFIED` for fixed finite mode count and degree under the paper's
ideal-effective-evolution assumption.

Formal run `d73842bb-ced5-4f6b-8bf9-2bab57b1dcdd` executed commit
`6eebf0225e132b0579cd04018c935925e6f411a5` in 30 seconds on local CPU with
one numerical thread.

The complete two-mode degree-two Hamiltonian contained 14 independent real
parameters. Across seven predeclared RPE horizons and 24 replicates, median
coefficient RMSE had log-error/log-time slope `-0.999073`; a same-budget
physical `kappa=1` Ramsey control had slope `-0.493321`. The finest RPE median
RMSE was `5.4667e-5`.

The 121-dimensional finite-Fock audit applied actual two-mode displacement and
independent local twirling: vacuum-constant error was `5.55e-17` and the
twirled off-diagonal norm was zero. Omitting twirl left norm `12.6178`;
omitting displacement left coefficient RMSE `0.101740`. The independent
checker passed and a tampered acceptance field made it exit one.
