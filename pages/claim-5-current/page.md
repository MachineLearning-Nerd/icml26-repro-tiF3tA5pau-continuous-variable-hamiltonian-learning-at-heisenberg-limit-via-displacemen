# Claim 5: Bogoliubov squeezing search

Status: **VERIFIED** for the paper's conditional logarithmic bisection theorem.

This page supersedes the generic `f(x)=x²` exercise in
[Historical rejected baseline](#/verification-run). That function does not
even provide a sign-changing bracket on the historical interval. The old page
remains preserved and reachable, but it is not the current verifier.

## Exact claim and source

The physical and reference modes obey Equation (71),

`B=B' cosh(Delta R)+B'† sinh(Delta R)`.

When a coefficient is known to vanish in the physical basis and has nonzero
response to basis mismatch, Section 5.3 proposes an outer bisection whose
queries run the D-RUT/RPE inner loop. Equations (77)-(78) require the signal to
remain resolvable above inner-loop error. Conditional on a valid bracket and
reliable signal signs, the claimed iteration count is
`O(log(1/epsilon_R))`.

Source: arXiv:2510.08419v1, PDF SHA-256
`88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7`.
Anchors: Section 5.3, Equations (71)-(78), and the Section 6.1 inner/outer
loops. The exact assumptions and version audit are in the
[source audit](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_5/source_audit.md).

The executable contract uses `H=omega B†B`, search interval `[0,0.4]`, and
true squeezing `sqrt(3)/10`. The interval contains the solution; `g'20` is
known to vanish in the physical basis; its response is nonzero; the printed
RPE-overlap condition passes; and an independently calibrated D-RUT/RPE
oracle supplies signal signs.

## Physical signal and proof certificate

Substituting the Bogoliubov relation and normal-ordering gives the actual
paper signal

```text
g'20(Delta R) = omega sinh(Delta R) cosh(Delta R)
              = (omega/2) sinh(2 Delta R).
```

SymPy verified the identity exactly, `g'20(0)=0`, and
`d g'20/d Delta R |0 = omega` (with `omega=1`). It is strictly monotone.
The overlap audit gave left side `2.030075` and allowed right side
`3.732051`.

For any valid initial bracket of width `W`, exact bisection gives width
`W/2^n` and midpoint error at most `W/2^(n+1)`. Therefore

```text
n = ceil(log2(W/(2 epsilon_R))),
```

which proves the conditional logarithmic iteration statement rather than
inferring it from a convenient finite curve.

Each noisy sign query builds the mismatched Hamiltonian in a 24-state Fock
basis, applies physical displacement at three Chebyshev radii, performs a
29-phase number twirl, samples X/Y ancilla outcomes at power-of-two RPE
horizons, and recovers `g'20` from the angular contrast. Executable source:
[claim5.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_5/claim5.py),
[faithful_drut.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_5/faithful_drut.py),
and independent
[claim5_verify.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_5/claim5_verify.py).
The environment is pinned by
[pyproject.toml](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_5/pyproject.toml)
and [uv.lock](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_5/uv.lock).

Exact cumulative command:

```bash
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

Seed: `505251008419`. Git SHA:
`72518d15b683b450274406736e0bbe3488c09800`. OpenResearch run:
`a18c9a9f-82fc-41a0-bc03-27786fc277f8`.

## Independent calibration and raw result

The inner RPE horizon was not selected from the formula being tested. Five
predeclared horizons were swept on a separate `|Delta R|=2e-4` sign task.
Level 8 failed (`52/64`, Wilson lower `0.700254`); level 10 was the first
success (`64/64`, lower `0.943374`) and was frozen before disjoint validation.

| Target `epsilon_R` | Exact iterations | Validation | Wilson 95% lower |
| ---: | ---: | ---: | ---: |
| 0.050000 | 2 | 32/32 | 0.892817 |
| 0.025000 | 3 | 32/32 | 0.892817 |
| 0.012500 | 4 | 32/32 | 0.892817 |
| 0.006250 | 5 | 32/32 | 0.892817 |
| 0.003125 | 6 | 32/32 | 0.892817 |

The iteration slope against `log2(1/epsilon_R)` was `1.000000`.
Finite-Fock response error was `3.89e-16`; maximum twirl off-diagonal
Frobenius norm was `6.93e-15`. Every trial, RPE record, exact certificate,
resource count, and acceptance boolean is in the downloadable
[raw JSON](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_5/raw_results.json).

The independent checker returned:

```json
{"checker":"claim5_verify.py","failures":[],"passed":true}
```

Download the
[checker output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_5/checker_output.json).
A tampered `bogoliubov_signal_identity_is_exact=false` copy made the checker
exit one:

```json
{"checker":"claim5_verify.py","failures":["bogoliubov_signal_identity_is_exact"],"passed":false}
```

Download the
[tamper output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_5/tamper_test_output.json).

## Negative controls

Three controls fail for distinct intended reasons:

- the underpowered RPE level 8 fails the predeclared confidence threshold;
- setting the response coefficient to zero gives endpoint signs `[0,0]`, the
  paper's barren-plateau case; and
- the historical `x²` proxy gives endpoint values `[0,0.16]`, not a
  sign-changing bracket.

Download the exact
[control output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_5/negative_control_output.json).

## Compute and limitations

Estimated CPU requirement: one core and under five minutes. Selected backend:
local CPU; numerical libraries were capped to one thread on an
eight-core-visible host. The OpenResearch run took 30 seconds; Claim 5 itself
took 1.818 seconds after environment setup and cumulative checks. The
simulation represented `34,406,400` ancilla shots and total evolution time
`38,349,766,656` analytically rather than looping over individual shots.

The proof is conditional on a bracket and sign-informative oracle, exactly as
the source is. The physical instance is the auditable number Hamiltonian, not
every first-quantization Hamiltonian. This claim does not establish Theorem
2's total evolution-time scaling. See
[limitations](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_5/limitations.md)
and the exact
[claim contract](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_5/claim_contract.json).
