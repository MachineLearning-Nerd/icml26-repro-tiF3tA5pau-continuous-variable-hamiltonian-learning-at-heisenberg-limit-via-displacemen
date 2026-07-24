# Claim 1: multi-mode Heisenberg scaling

Status: **VERIFIED** for fixed finite mode count and degree under the paper's
ideal-effective-evolution assumption.

This page supersedes the historical random linear system with injected `1/T`
noise in [Historical rejected baseline](#/verification-run). The current
verifier executes physical bosonic displacement, independent random-unitary
twirling, sampled X/Y robust phase estimation, Chebyshev/IDFT recovery, and
hierarchical coupling recovery. The old page remains preserved but is not the
current verifier.

## Exact claim and source

Theorem 1 states that, given unitary access to the generic finite-order
multi-mode Hamiltonian of Equation (1), D-RUT learns all coefficients to RMSE
`epsilon` with total evolution time `O(epsilon^-1)`.

Source: arXiv:2510.08419v1, PDF SHA-256
`88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7`.
Anchors: Theorem 1, Equation (1), Equations (9)-(30), and Section 4.
The [source audit](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_1/source_audit.md)
records the quantifiers and assumptions.

The executable instance is the complete two-mode, total-degree-two Hermitian
family: ten independent real single-mode parameters and four independent
pair/hopping coupling parameters. No coefficient in that family is omitted.
The proof certificate addresses the theorem's fixed finite `N,d` asymptotic
quantifier.

## Implemented protocol

For each mode, three Chebyshev radii and all Algorithm 1 angles feed the
paper's radial interpolation and IDFT. Eight joint complex displacements
produce coupling constants; single-mode estimates are subtracted before a
full-rank coupling solve, implementing the hierarchical Section 4 path.

At every point, the verifier samples binomial ancilla outcomes from the
paper's exact probabilities

```text
P_X(0)=(1+cos(kappa C(beta)))/2,
P_Y(0)=(1+sin(kappa C(beta)))/2
```

at `kappa=1,2,...,2^J`, unwraps phase, and recovers all 14 coefficients.
The physical audit separately constructs the 121-dimensional two-mode
Hamiltonian, applies matrix-exponential displacement, and performs an exact
13-by-13 independent cyclic number twirl.

Executable source:
[claim1.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_1/claim1.py),
[faithful_drut.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_1/faithful_drut.py),
and independent
[claim1_verify.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_1/claim1_verify.py).
The environment is pinned by
[pyproject.toml](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_1/pyproject.toml)
and [uv.lock](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_1/uv.lock).

Exact cumulative command:

```bash
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

Seed: `101251008419`. Git SHA:
`6eebf0225e132b0579cd04018c935925e6f411a5`. OpenResearch run:
`d73842bb-ced5-4f6b-8bf9-2bab57b1dcdd`.

## Resource certificate and observed scaling

For `S=256` shots per X/Y basis, one response at horizon `J` uses exactly

```text
T_J = 2 S sum_(j=0)^J 2^j = 2S(2^(J+1)-1).
```

The design contains a fixed 32 responses for fixed `N=2,d=2`; its point count
and inverse-design norm do not depend on `epsilon`. Thus multiplying
per-response `O(1/epsilon)` RPE time by the fixed design preserves
`O(1/epsilon)`. The monomial certificate independently expands displacement,
twirls unequal powers away, and recovers vacuum constant
`(beta*)^p beta^q`.

No error curve was injected. Seven fixed horizons were each run with 24
independent seeds:

| Total evolution time | Median D-RUT/RPE RMSE | Same-budget Ramsey RMSE |
| ---: | ---: | ---: |
| 2,080,768 | 3.4935e-3 | 2.1730e-2 |
| 4,177,920 | 1.7291e-3 | 1.8242e-2 |
| 8,372,224 | 9.3312e-4 | 1.2017e-2 |
| 16,760,832 | 4.3255e-4 | 8.6046e-3 |
| 33,538,048 | 2.7085e-4 | 6.5548e-3 |
| 67,092,480 | 9.9356e-5 | 4.1420e-3 |
| 134,201,344 | 5.4667e-5 | 2.9218e-3 |

The D-RUT/RPE slope was `-0.999073`; the same-budget conventional Ramsey
slope was `-0.493321`. Every replicate and resource count is downloadable in
[raw JSON](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_1/raw_results.json).

The independent checker reconstructed both slopes and the exact resource
schedule:

```json
{"checker":"claim1_verify.py","failures":[],"passed":true}
```

Download the
[checker output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_1/checker_output.json).
A false Heisenberg-slope acceptance field made it exit one:

```json
{"checker":"claim1_verify.py","failures":["rpe_coefficient_slope_is_heisenberg"],"passed":false}
```

Download the
[tamper output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_1/tamper_test_output.json).

## Physical audit and controls

| Check | Observed |
| --- | ---: |
| Hamiltonian Hermiticity residual | `0` |
| displaced/twirled vacuum-constant error | `5.55e-17` |
| twirl off-diagonal Frobenius norm | `0` |
| coupling design rank | `4/4` |
| omit-displacement coefficient RMSE | `0.101740` |
| omit-twirl off-diagonal Frobenius norm | `12.617756` |

The Ramsey control uses the identical evolution-time budget and actual X/Y
ancilla sampling at `kappa=1`; it is not synthetic `1/sqrt(T)` noise. The
other controls fail because displacement encodes non-number-conserving
coefficients and twirling makes the vacuum an eigenstate. Download
[control output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_1/negative_control_output.json).

## Compute and limitations

Estimated requirement: one CPU core and under three minutes. The local backend
used an eight-core-visible host with numerical libraries capped to one thread.
The cumulative OpenResearch run took 30 seconds; Claim 1 itself took 2.100
seconds.

The result does not claim favorable scaling when `N` or `d` grows. The
finite-Fock physical audit uses cutoff 11. RPE samples the paper's ideal
effective evolution; gate synthesis and finite-Trotter errors are outside this
result, matching the theorem's assumption that `L` is sufficiently large.
See the exact
[claim contract](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_1/claim_contract.json)
and
[limitations](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_1/limitations.md).
