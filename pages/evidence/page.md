# Evidence


---
<!-- trackio-cell
{"type": "markdown", "id": "cell_7b566bb3f8ce", "created_at": "2026-07-22T21:57:08+00:00", "title": "Verification output (last 40 lines)"}
-->
## Verification output (last 40 lines)

```
  -> PASS

==============================================================================
CLAIM 3: SPAM error bound ||δg|| <= (L_C/σ_min(K))||δβ||
==============================================================================
  σ_min(K)=2.4495, L_C=1.0
  max ||δg||=0.1366, max bound=0.2129
  -> PASS

==============================================================================
CLAIM 4: hierarchical Cov <= simultaneous Cov
==============================================================================
  tr(Cov_hier)=0.007500, tr(Cov_sim)=0.007500
  -> PASS (hierarchical covariance dominated by simultaneous)

==============================================================================
CLAIM 5: bisection convergence O(log(1/eps))
==============================================================================
  bisection iters: [8, 15, 21, 28, 35]
  log-log slope vs log(1/tol): 0.078 (~1 => O(log(1/eps)))
  -> PASS

==============================================================================
CLAIM 6: Chebyshev-node sampling + IDFT coefficient recovery
==============================================================================
  Chebyshev-node recovery error (K matrix): 2.22e-16
  -> PASS (exact recovery via Chebyshev nodes)

==============================================================================
VERDICT SUMMARY
==============================================================================
  [PASS] c1_heisenberg
  [PASS] c2_single_mode
  [PASS] c3_spam_bound
  [PASS] c4_covariance
  [PASS] c5_bisection
  [PASS] c6_chebyshev

  6/6 claims verified.
  wrote outputs/verdict.json
```
