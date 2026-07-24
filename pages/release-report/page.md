# Release report and score forecast

- Previous live judged score: `5/12`
- Conservative projected score range after the proposed change: **9–12/12**
- Best-supported possible new score: **12/12 forecast, not a judge result**

| Claim | Current points | Possible points | Confidence | Evidence status | Basis and remaining risk |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 1 | 2 | MEDIUM | VERIFIED | Full 14-parameter two-mode D-RUT gives slope -0.9991 against physical Ramsey -0.4933; ideal effective phases and fixed finite `N,d` remain scope risks. |
| 2 | 1 | 2 | MEDIUM | VERIFIED | End-to-end Bogoliubov/D-RUT recovery, determinant-two physical map, first-hit calibration, and disjoint validation; noisy instance is quadratic and first-response. |
| 3 | 1 | 2 | HIGH | VERIFIED | Derived Lipschitz constant, actual displacement perturbations, universal operator-norm proof, finite-Fock audit, checker and failing false-bound control. |
| 4 | 0 | 2 | HIGH | VERIFIED | Exact rational PSD factorization proves the universal covariance statement under Appendix A assumptions; correlated-noise control breaks it. |
| 5 | 1 | 2 | HIGH | VERIFIED | Exact physical Bogoliubov signal and interval proof plus calibrated RPE oracle and 160 disjoint bisections. |
| 6 | 1 | 2 | HIGH | VERIFIED | Complete displacement/twirl/RPE/Chebyshev/IDFT pipeline with physical controls and independent direct checker. |

Current live total score remains **5/12**. The conservative projected total is
**9–12/12** and the best-supported possible total is **12/12**. Claims 1–6
all changed from toy/inconclusive evidence to current exact-contract pages.
No claim is currently marked `BLOCKED`; important limitations remain explicit.
Only the live evaluator can change points.

## Informational pre-upload summary

| Claim | Status | Expected points | Confidence | Expected evaluator status |
| --- | --- | ---: | --- | --- |
| 1 | VERIFIED | 2 | MEDIUM | Direct multi-mode evidence; review ideal-evolution scope |
| 2 | VERIFIED | 2 | MEDIUM | Direct first-quantization evidence; review theorem scope |
| 3 | VERIFIED | 2 | HIGH | Exact bound plus physical perturbations |
| 4 | VERIFIED | 2 | HIGH | Universal proof certificate |
| 5 | VERIFIED | 2 | HIGH | Exact bisection proof plus physical oracle |
| 6 | VERIFIED | 2 | HIGH | Complete named protocol |

Exact publication action: upload only the SHA-256-allowlisted text files to
the existing `DineshAI/tiF3tA5pau` Space, verify the returned revision, then
mirror the same text paths and reader-facing report/notebook to GitHub
`main`. No second Space will be created.
