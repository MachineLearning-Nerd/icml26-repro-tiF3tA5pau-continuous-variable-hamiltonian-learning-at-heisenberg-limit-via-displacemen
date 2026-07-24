# Claim 6: current D-RUT pipeline

Status: **VERIFIED** within the exact finite-Fock Claim 6 contract.

This page supersedes the interpolation-only page labeled
[Historical rejected baseline](#/verification-run). That page and its original
evidence remain reachable and unchanged.

## Exact claim and source

> The algorithm uses Chebyshev-node sampling of the displacement parameter
> combined with robust phase estimation and inverse discrete Fourier transform
> to reconstruct coefficients, as detailed in Algorithm 1 and illustrated for
> the single-mode case in Figure 1.

Source version: arXiv:2510.08419v1, PDF SHA-256
`88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7`.
Anchors: Algorithm 1, Figure 1, Equation (2), and Equations (24)-(30).
The [source audit](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_6/source_audit.md)
documents the v1/v2 discrepancy, assumptions, and quantifiers.

## What was executed

The verifier followed every named stage:

1. Build a nontrivial Hermitian degree-2 bosonic Hamiltonian in a 24-state Fock
   representation.
2. Form the physical displacement matrix
   `D(beta) = exp(beta b† - beta* b)`.
3. Average over 29 number rotations, exactly implementing the U(1) projection
   for every index difference in the truncated representation.
4. Sample the paper's X/Y ancilla probabilities at
   `kappa = 1, 2, ..., 4096` with 256 shots per basis and level.
5. Estimate each scalar response with iterative robust phase unwrapping.
6. Sample three mapped Chebyshev radii for each required paper angle.
7. Recover radial coefficients, then apply Equation (30)'s inverse DFT.

The full executable source is visible in
[claim6.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_6/claim6.py),
[faithful_drut.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_6/faithful_drut.py),
and the independent
[claim6_verify.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_6/claim6_verify.py).
The exact environment is pinned in
[pyproject.toml](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_6/pyproject.toml)
and [uv.lock](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_6/uv.lock).

Exact command:

```bash
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

Seed: `251008419`. Git SHA:
`90cbb933ed2d4d8775b78185823412a8536bcbf0`. OpenResearch run:
`bbf94f9d-627f-4af6-9d56-88baeb6004b5`.

## Raw result

| Check | Predeclared requirement | Observed |
| --- | ---: | ---: |
| Hamiltonian Hermiticity residual | `< 1e-12` | `0` |
| Fock D-RUT vs analytic `C(beta)` max error | `< 2e-6` | `1.11e-16` |
| Twirl off-diagonal Frobenius norm | `< 2e-10` | `5.49e-15` |
| Algorithm 1 coefficient RMSE | `< 2.5e-3` | `9.54e-5` |
| Independent full-design RMSE | `< 2.5e-3` | `2.26e-5` |
| Production/checker RMSE | `< 2.5e-3` | `9.80e-5` |

All measurements, every RPE count, recovered coefficients, resources, and
acceptance booleans are in the downloadable
[raw JSON](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_6/raw_results.json).

The independent checker returned:

```json
{"checker":"claim6_verify.py","passed":true,"failures":[]}
```

Download the
[checker output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_6/checker_output.json).
Its verifier exits nonzero if any acceptance boolean is false or the verdict is
not `VERIFIED`. A tampered copy with one acceptance boolean forced false exited
nonzero and returned:

```json
{"checker":"claim6_verify.py","passed":false,"failures":["algorithm1_coefficient_rmse_below_threshold"]}
```

Download the
[tamper-test output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_6/tamper_test_output.json).

## Negative controls

| Omitted component | Intended failure | Observed |
| --- | --- | ---: |
| Displacement | Nonzero coefficients cannot be reconstructed | coefficient RMSE `0.21180` |
| Number-rotation twirl | Vacuum is not a scalar-eigenphase probe | leakage probability `0.13413` |

Both controls failed for the intended physical reason. Download the
[control output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_6/negative_control_output.json).

## Compute and limitations

Estimated CPU requirement: one core, under five minutes. Selected backend:
local CPU, no reservable flavor. The host exposed eight cores, while BLAS and
OpenMP were capped to one thread. OpenResearch wall duration was 20 seconds;
the inner verifier took 0.0118 seconds after environment setup.

This is simulated finite-Fock evidence, not a hardware experiment. Ancilla
outcomes are genuine deterministic-seed binomial samples from the quantum
response model. The D-RUT twirl is exact on the 24-state truncation, but
finite-`L` Trotter scaling is outside this claim. The experiment verifies the
Algorithm 1 composition on a degree-2 instance; it does not establish the
universal complexity theorems in Claims 1 or 2. See the full
[limitations](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_6/limitations.md).
