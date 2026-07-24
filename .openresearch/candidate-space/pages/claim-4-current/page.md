# Claim 4: covariance domination certificate

Status: **VERIFIED** under the exact full-rank, independent isotropic-noise
contract in Appendix A.

This page supersedes the covariance trace check in
[Historical rejected baseline](#/verification-run). The historical page used a
`1.1×` tolerance and happened to choose an equality case. It remains preserved
and reachable, but it is not the current verifier.

## Exact claim and source

> The hierarchical strategy learns single-mode coefficients first and coupling
> coefficients second, with
> `Cov(delta g)_hierarchical <= Cov(delta g)_simultaneous` for all parameters.

Source version: arXiv:2510.08419v1, PDF SHA-256
`88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7`.
Anchors: Section 4.1 and Appendix A, Equations (92)-(108). The
[source audit](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_4/source_audit.md)
records the exact rank, noise, independence, and version assumptions.

The executable contract tests the universal statement for every block design
`[M1 M2]` with full column rank, where the two hierarchical datasets are
independent and all compared measurement noises have the same isotropic
variance. These are the assumptions used by the inverses and covariance
algebra in Appendix A.

## Proof certificate

Let

`A=M1†M1`, `B=M1†M2`, `D=M2†M2`,
`Q=D-B†A^{-1}B`, and
`Z=[A^{-1}B; -D^{-1}B†A^{-1}B]`.

The verifier reconstructs the complete hierarchical estimator, including the
cross-covariance induced when the stage-one estimate is subtracted in stage
two. It then proves

```text
Cov_sim - Cov_hier = Z Q^{-1} Z† ⪰ 0.
```

The full-rank joint Gram matrix makes its Schur complement `Q` positive
definite, so the displayed factorization is a proof for the universal
quantifier—not an inference from a finite sweep.

SymPy checked the identity exactly over rational matrices. In the certificate,
the leading principal minors of `Q` were `89/23` and `24/23`, both positive,
and the nonzero difference matrix exactly equaled the factorized matrix.

Executable source:
[claim4.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_4/claim4.py)
and independent
[claim4_verify.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_4/claim4_verify.py).
The exact environment is pinned in
[pyproject.toml](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_4/pyproject.toml)
and [uv.lock](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_4/uv.lock).

Exact cumulative command:

```bash
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

Seed: `404251008419`. Git SHA:
`a4ee0f57a08560f2ca47f2a804c1f48f90aa96c5`. OpenResearch run:
`99068394-4336-4f8a-aa33-c20453a79c86`.

## Raw result

| Check | Predeclared requirement | Observed |
| --- | ---: | ---: |
| Exact rational factor identity | exact equality | passed |
| `Q` positive by Sylvester criterion | both minors positive | `89/23`, `24/23` |
| Strict-case trace improvement | `> 1e-6` | `6.288043478` |
| Strict-case identity residual | `< 2e-10` | `2.17e-14` |
| Strict-case minimum eigenvalue | `> -2e-10` | `-2.74e-16` |
| 64-case worst identity residual | `< 2e-10` | `2.99e-13` |
| 64-case worst minimum eigenvalue | `> -2e-10` | `-3.99e-15` |
| Monte Carlo covariance relative error | `< 0.03` | `0.003974` |
| Historical orthogonal equality norm | `< 2e-10` | `0` |

All exact matrices, assumptions, dimensions, metrics, resources, and
acceptance booleans are in the downloadable
[raw JSON](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_4/raw_results.json).

The independent checker returned:

```json
{"checker":"claim4_verify.py","failures":[],"passed":true}
```

Download the
[checker output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_4/checker_output.json).
Its verifier exits nonzero if any acceptance boolean is false or the verdict is
not `VERIFIED`. A tampered copy with the exact-identity acceptance boolean
forced false exited one and returned:

```json
{"checker":"claim4_verify.py","failures":["exact_rational_matrix_identity"],"passed":false}
```

Download the
[tamper-test output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_4/tamper_test_output.json).

## Controls and the historical equality

The historical equal traces are not hidden or reinterpreted. The current
verifier reproduces them exactly when `M1†M2=0`: the two methods coincide, as
“lower or equal” permits. A separate non-orthogonal case supplies strict
improvement.

The negative control reuses the same observation noise in both stages,
violating Appendix A's explicit independence assumption. The minimum
eigenvalue of `Cov_sim-Cov_hier` becomes `-0.132782` (determinant `-0.25`), so
domination fails for the intended reason. Download the
[control output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_4/negative_control_output.json).

## Compute and limitations

Estimated CPU requirement: one core and under five minutes. Selected backend:
local CPU, with BLAS/OpenMP capped to one thread. The host exposed eight cores.
OpenResearch wall duration was 20 seconds; the Claim 4 verifier itself took
0.103 seconds after environment setup and cumulative Claim 6 execution.

This certificate verifies the paper's linear covariance model. It does not
assert that hardware noise is isotropic or independent. Rank-deficient designs
would require a separate pseudoinverse theorem. See the complete
[limitations](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_4/limitations.md).
