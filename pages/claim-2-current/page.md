# Claim 2: first-quantization recovery

Status: **VERIFIED** for the exact quadratic first-quantization instance and
the fixed-finite-degree invertible-basis certificate.

This supersedes the historical one-number linear proxy in
[Historical rejected baseline](#/verification-run). The current code executes
the Bogoliubov outer loop, displacement/RPE inner queries, and physical
position/momentum coefficient recovery.

## Claim, assumptions, and source

Theorem 2 claims recovery of all real symmetrized `x,p` coefficients to RMSE
`epsilon_G` in
`O(log(1/epsilon_G))/epsilon_G` evolution time, assuming a known-zero
coefficient, finite nonzero response to basis mismatch, and a sufficiently
close reference.

Source: arXiv:2510.08419v1, PDF SHA-256
`88c58a90096ad67bea10336322a33d15a76367d59a7195ef30266c702652b2c7`;
anchors Theorem 2, Equations (4)-(7), and (71)-(85). See the
[source audit](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/source_audit.md).

The physical instance is
`H=G20 x²+G02 p²`. In its physical oscillator basis, `g20=0`; under mismatch,

```text
g20=(omega/2)sinh(2 DeltaR),  g11=omega cosh(2 DeltaR).
```

SymPy certified the zero and derivative `omega != 0`. The overlap audit was
`2.030075 < 3.732051`. The exact quadratic map from
`[Re(g20),Im(g20),g11]` to `[G20,G11,G02]` has determinant `2`, proving that
the run recovers physical coefficients rather than only a squeezing root.
For fixed finite degree, a canonical Bogoliubov change of basis remains an
invertible finite linear map.

Source code:
[claim2.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/claim2.py),
[claim2_verify.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/claim2_verify.py), and
[faithful_drut.py](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/faithful_drut.py).
Pinned environment:
[pyproject.toml](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/pyproject.toml),
[uv.lock](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/uv.lock).

Exact cumulative command:

```bash
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

Seed `202251008419`; Git SHA `337c9b256ef4049ad295582d7818f00fa4d7050e`;
run `826fd8e2-da51-4bcc-8f0d-a2fe1650d046`.

## Independent calibration and result

Eight-to-ten predeclared RPE horizons were swept on calibration seeds. The
first level with 16/16 successes and median RMSE at most target/3 was frozen
for 32 disjoint trials.

| Target RMSE | First-hit level | Median time | Median observed RMSE | Success (Wilson lower) |
| ---: | ---: | ---: | ---: | ---: |
| 0.0050000 | 6 | 1,040,384 | 7.8306e-4 | 32/32 (0.8928) |
| 0.0025000 | 8 | 4,709,376 | 4.2564e-4 | 32/32 (0.8928) |
| 0.0012500 | 8 | 5,232,640 | 2.9003e-4 | 32/32 (0.8928) |
| 0.0006250 | 9 | 11,523,072 | 1.3208e-4 | 32/32 (0.8928) |
| 0.0003125 | 10 | 25,153,536 | 1.1193e-4 | 31/32 (0.8426) |

After dividing out the exact logarithmic bisection factor, log evolution time
versus log inverse target had slope `0.896740`. All raw calibration and
validation trials are in
[raw JSON](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/raw_results.json).

The independent checker reconstructed the slope, first hits, and determinant:

```json
{"checker":"claim2_verify.py","failures":[],"passed":true}
```

[Checker output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/checker_output.json).
Tampering with transform invertibility made it exit one:

```json
{"checker":"claim2_verify.py","failures":["quadratic_physical_transform_is_exactly_invertible"],"passed":false}
```

[Tamper output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/tamper_test_output.json).

## Controls, compute, and limits

At the finest target, level 5 was underpowered: 5/16 success, Wilson lower
`0.1416`. A zero-response signal cannot supply a sign, and deleting a row of
the physical transform makes it rank deficient. Exact values:
[control output](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/negative_control_output.json).

The first coarse-target route is preserved as
[blocked attempt](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/attempt_1_blocked.md);
no threshold was relaxed. The accepted cumulative run used one capped local
CPU thread and took about 35 seconds; Claim 2 itself took 2.885 seconds.

The noisy instance uses a first-order quadratic signal. Higher-order signals,
finite-Trotter error, and hardware synthesis are not empirically covered. See
[limitations](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/limitations.md)
and the [contract](https://huggingface.co/spaces/DineshAI/tiF3tA5pau/blob/main/evidence/claim_2/claim_contract.json).
