# Claim 4 method

The verifier reconstructs the exact linear estimators in Appendix A. The
simultaneous estimator uses the inverse joint Gram matrix. The hierarchical
estimator uses one independent dataset for `M1`, then a second independent
dataset for `M2` after subtracting the stage-one prediction. Its covariance is
formed from the complete estimator map, so the stage-one/stage-two
cross-covariance is not discarded.

Three complementary checks are used:

1. SymPy evaluates the factorization
   `Cov_sim-Cov_hier=Z Q^{-1} Z^T` exactly over rational matrices and certifies
   `Q` positive definite by Sylvester's criterion.
2. NumPy evaluates one strict non-orthogonal case and 64 seeded random
   full-rank designs across several block dimensions. A 50,000-sample
   Monte Carlo experiment independently checks the analytic hierarchical
   covariance.
3. An orthogonal-block case reproduces the exact equality seen in the
   historical rejected baseline. It is a boundary case, not evidence of a
   strict gain.

The negative control deliberately violates Appendix A's independent-stage
noise assumption by reusing identical measurement noise. The covariance
domination must then break. This shows the acceptance rule is sensitive to a
substantive theorem assumption rather than merely checking a generic inverse
matrix identity.

All stochastic checks use seed `404251008419`. The symbolic identity, rather
than the finite random sweep, is the evidence for the universal quantifier.
