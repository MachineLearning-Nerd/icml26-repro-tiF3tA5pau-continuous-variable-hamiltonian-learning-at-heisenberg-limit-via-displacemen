# Claim 3: displacement-SPAM bound

Status: **VERIFIED** for the exact displacement-miscalibration model and
bounded domain in Section 3.6.

This page supersedes the arbitrary-`L_C=1` inverse-matrix exercise in
[Historical rejected baseline](#/verification-run). That historical evidence
remains preserved and reachable but is not the current verifier.

## Exact claim and source

For actual displacements
`beta_tilde_j=beta_j+delta beta_j`, Equations (36)-(40) define

`delta g_SPAM=K^+[C(beta_tilde)-C(beta)]`,

separately from RPE statistical noise. Equation (43) states

```text
||delta g_SPAM||_2 <= L_C/sigma_min(K) ||delta beta||_2.
```

Source version: arXiv:2510.08419v1, PDF SHA-256
`88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7`.
Anchors: Section 3.6, Equations (36)-(46). The
[source audit](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_3/source_audit.md)
records the exact quantifiers and assumptions.

The contract covers a single-mode Hermitian degree-2 Hamiltonian, the actual
combined Algorithm 1 Chebyshev/angular design `K`, and all displacement
perturbations whose line segments stay inside `|beta|<=0.70`. RPE noise is
excluded because Equation (40) defines it as a separate term.

## The physical response and derived constant

For `beta=x+i y` and independent physical parameters
`[a,b,c,d,e]=[Re(g10),Im(g10),Re(g20),Im(g20),g11]`, the displaced-and-twirled
D-RUT response is

```text
C(x,y)=2ax+2by+2c(x²-y²)+4dxy+e(x²+y²).
```

SymPy differentiated this exact polynomial. Its gradient is affine,
`grad C=h+H[x,y]`, with

```text
h = [0.40, 0.16]
H = [[ 0.94, -0.12],
     [-0.12,  0.46]]
```

On the certified disk, the triangle and spectral-norm inequalities give

`L_C=||h||_2+||H||_2(0.70)=1.1086428947`.

This replaces the historical arbitrary value. The actual 12-by-5 Algorithm 1
design has rank 5,
`sigma_min(K)=0.1912623836`, and
`||K^+||_2=5.2284196247=1/sigma_min(K)`.

The universal proof is the composition of the mean-value inequality,
the block-diagonal vector-response Lipschitz bound, and the pseudoinverse
operator norm. The finite sweep below corroborates the physical
implementation; it is not used to infer the universal quantifier.

Executable source:
[claim3.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_3/claim3.py),
[faithful_drut.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_3/faithful_drut.py),
and independent
[claim3_verify.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_3/claim3_verify.py).
The environment is pinned in
[pyproject.toml](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_3/pyproject.toml)
and [uv.lock](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_3/uv.lock).

Exact cumulative command:

```bash
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

Seed: `303251008419`. Git SHA:
`3f66f82603c3bb6b71e4afbc67abd40b2e3f9756`. OpenResearch run:
`6d6f78f3-b9b5-4ed3-bbb3-15bd6da140fc`.

## Raw result

Twelve seeded perturbation directions were each evaluated at five fixed
magnitudes. Pairing direction across scale avoids a direction-amplification
confound.

| Check | Predeclared requirement | Observed |
| --- | ---: | ---: |
| Symbolic D-RUT response gradient | exact | passed |
| Combined design rank | `5` | `5` |
| Finite-Fock vs analytic response max error | `< 2e-12` | `5.55e-16` |
| Twirl off-diagonal Frobenius max | `< 2e-10` | `5.59e-15` |
| Eq. 43 trials | all 60 pass | all passed |
| Maximum error/bound ratio | `<= 1.0000000001` | `0.175944` |
| Paired median-error log-log slope | `[0.94,1.06]` | `1.000489` |

Median coefficient-SPAM errors for perturbation norms
`[1e-4,3e-4,1e-3,3e-3,1e-2]` were
`[6.753e-5,2.026e-4,6.755e-4,2.028e-3,6.770e-3]`.

Every trial, exact symbolic expression, singular value, resource, and
acceptance boolean is in the downloadable
[raw JSON](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_3/raw_results.json).

The independent checker reconstructed `L_C`, checked
`||K^+||=1/sigma_min`, traversed every raw trial, and returned:

```json
{"checker":"claim3_verify.py","failures":[],"passed":true}
```

Download the
[checker output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_3/checker_output.json).
A tampered symbolic-gradient acceptance boolean made it exit one:

```json
{"checker":"claim3_verify.py","failures":["symbolic_d_rut_response_gradient_is_exact"],"passed":false}
```

Download the
[tamper-test output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_3/tamper_test_output.json).

## Negative control and rejected attempt

The negative control uses an adversarial local perturbation direction but
replaces the derived constant by `L_C/1000`. The observed coefficient error
was `3.3161e-5`, while the false bound was `5.7965e-8`: a violation ratio of
`572.09`. Download the
[control output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_3/negative_control_output.json).

The first formal attempt changed random directions at every magnitude. Its
optional slope was `0.927979`, outside the fixed interval, even though all
Equation (43) checks passed. It remains transparently documented as a rejected
design in
[attempt 1](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_3/attempt_1_failed.md).

## Compute and limitations

Estimated CPU requirement: one core, under five minutes. Selected backend:
local CPU; BLAS/OpenMP were capped to one thread on an eight-core-visible host.
OpenResearch wall duration was 25 seconds; Claim 3 itself took 1.029 seconds
after environment setup and cumulative checks.

The certified `L_C` is a safe upper bound, not claimed minimal. This result
does not cover arbitrary state-preparation or readout channels, unbounded
displacements, or the separately modeled RPE statistical term. See the full
[limitations](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_3/limitations.md).
