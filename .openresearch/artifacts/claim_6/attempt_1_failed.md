# Attempt 1: aliased finite twirl

- Experiment: `Claim 6 faithful D-RUT pipeline`.
- Commit: `af5de2242a79ac239b312a54fd26e2b48f02837c`.
- Run: `094aaa3f-1884-4c45-a361-3045555e28ad`.
- Backend: local CPU; one-thread cap.
- Formal result: exit 1, `BLOCKED`.

All coefficient and control checks passed:

- Algorithm 1 coefficient RMSE: `9.5413e-5`.
- Independent full-design RMSE: `2.2559e-5`.
- Production/checker RMSE: `9.8048e-5`.
- Fock-vs-analytic constant maximum error: `1.6653e-16`.
- Omit-displacement RMSE: `0.21180`.
- Omit-twirl vacuum leakage probability: `0.13413`.

The seven-point number-rotation average failed the diagonalization check with
off-diagonal Frobenius norm `0.042749`. Although degree two bounds the ideal
displaced polynomial's number differences, forming the displacement as a
truncated matrix exponential creates boundary terms across the finite matrix.
The seven-point cyclic average aliases differences divisible by seven.

The correction is mathematical rather than threshold tuning: a cyclic average
with more phases than the largest possible nonzero Fock-index difference
implements the continuous U(1) projection exactly on the finite matrix. The
child uses 29 phases for a 24-state cutoff and retains every acceptance
threshold.
