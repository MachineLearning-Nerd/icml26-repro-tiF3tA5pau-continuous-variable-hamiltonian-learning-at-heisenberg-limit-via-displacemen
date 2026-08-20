# Claim-by-claim D-RUT Hamiltonian-learning reproduction

## Collection classification and audit boundary

This repository is a **legacy/source workspace** for *Continuous-Variable Hamiltonian Learning at Heisenberg Limit via Displacement Randomized Unitary Transformations*
(arXiv `2510.08419`, OpenReview `tiF3tA5pau`). It is preserved
separately from the standardized canonical record at
[`icml26-d-rut-hamiltonian-learning`](https://github.com/MachineLearning-Nerd/icml26-d-rut-hamiltonian-learning).

The claim results and scores recorded below are historical results of this
workspace. They are not new paper-level verifications performed while
organizing the collection. The collection audit did not run the scientific
implementation; the canonical record documents its own scoped status and
limitations.

### How the historical claim evidence is produced

The claim table and experiment log below are the authoritative mapping from
each paper claim to its producer, command, control, and evidence artifact. In
this workspace, the D-RUT verification runner, claim-specific branches, covariance certificates, scaling fits, and IDFT/Bogoliubov checks feed the committed report and evidence surfaces.

The former `orx/*` branches are historical workstreams, not additional final
publication claims. Their purposes and tips are preserved in
[`BRANCH_AUDIT.md`](BRANCH_AUDIT.md). Citation and author acknowledgment
details are in [`CITATION.cff`](CITATION.cff) and
[`AUTHOR_THANK_YOU.md`](AUTHOR_THANK_YOU.md).

The previous judged artifact scored **5/12** because it replaced the quantum
protocol with injected-noise linear algebra. This campaign tests all six
claims of arXiv:2510.08419v1 with physical bosonic displacement, independent
number twirling, sampled robust phase estimation, Chebyshev/IDFT recovery,
Bogoliubov search, and proof certificates.

The headline two-mode experiment recovers all 14 degree-two parameters with
RMSE slope **-0.9991** versus total evolution time; a same-budget physical
Ramsey control gives **-0.4933**. All six current verifiers return `VERIFIED`,
but this is a forecast—not a new judge score. The simulations use local CPU,
one numerical thread, finite Fock cutoffs, and ideal effective phases rather
than finite-Trotter hardware circuits.

[Read the illustrated report](reports/drut-reproduction/report.md) ·
[Open the tutorial notebook](notebooks/drut_tutorial.py) ·
[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-tiF3tA5pau-continuous-variable-hamiltonian-learning-at-heisenberg-limit-via-displacemen/blob/main/notebooks/drut_tutorial.py)

The published evaluator artifact is mirrored at the same root-relative
`pages/`, `evidence/`, and `release/` paths. The Space metadata README is
preserved verbatim as [`hf-space-README.md`](hf-space-README.md); this GitHub
README intentionally remains the project landing page.

## Experiment log

Every row inherited the exact same command.

| Branch / experiment | Purpose | Exact run command | Assessment / outcome | Compute |
| --- | --- | --- | --- | --- |
| `main` | Public report and release surface | Not run as an experiment (publication surface) | Presentation only | — |
| [`orx/claim-6-exact-finite-u-1-twirl`](https://github.com/MachineLearning-Nerd/icml26-repro-tiF3tA5pau-continuous-variable-hamiltonian-learning-at-heisenberg-limit-via-displacemen/tree/orx/claim-6-exact-finite-u-1-twirl) | Complete Algorithm 1 D-RUT path | `uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py` | VERIFIED; coefficient RMSE `9.54e-5` | local CPU, 1 thread, 20s |
| [`orx/claim-4-covariance-proof-certificate`](https://github.com/MachineLearning-Nerd/icml26-repro-tiF3tA5pau-continuous-variable-hamiltonian-learning-at-heisenberg-limit-via-displacemen/tree/orx/claim-4-covariance-proof-certificate) | Exact covariance domination certificate | `uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py` | VERIFIED; exact PSD factorization | local CPU, 1 thread, 20s |
| [`orx/claim-3-paired-direction-scaling`](https://github.com/MachineLearning-Nerd/icml26-repro-tiF3tA5pau-continuous-variable-hamiltonian-learning-at-heisenberg-limit-via-displacemen/tree/orx/claim-3-paired-direction-scaling) | Actual D-RUT SPAM model | `uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py` | VERIFIED; Eq. 43 max ratio `0.1759` | local CPU, 1 thread, 25s |
| [`orx/claim-5-bogoliubov-bisection`](https://github.com/MachineLearning-Nerd/icml26-repro-tiF3tA5pau-continuous-variable-hamiltonian-learning-at-heisenberg-limit-via-displacemen/tree/orx/claim-5-bogoliubov-bisection) | Physical squeezing search | `uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py` | VERIFIED; iterations `[2,3,4,5,6]` | local CPU, 1 thread, 30s |
| [`orx/claim-1-multimode-heisenberg-scaling`](https://github.com/MachineLearning-Nerd/icml26-repro-tiF3tA5pau-continuous-variable-hamiltonian-learning-at-heisenberg-limit-via-displacemen/tree/orx/claim-1-multimode-heisenberg-scaling) | Generic two-mode scaling | `uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py` | VERIFIED; D-RUT `-0.9991`, Ramsey `-0.4933` | local CPU, 1 thread, 30s |
| [`orx/claim-2-finer-precision-calibration`](https://github.com/MachineLearning-Nerd/icml26-repro-tiF3tA5pau-continuous-variable-hamiltonian-learning-at-heisenberg-limit-via-displacemen/tree/orx/claim-2-finer-precision-calibration) | First-quantization outer/inner loop | `uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py` | VERIFIED; normalized resource slope `0.8967` | local CPU, 1 thread, ~35s |

## Reproduce

```bash
uv sync --frozen --no-dev
uv run --frozen python repro/src/verify_drut.py
marimo edit notebooks/drut_tutorial.py
```

The complete evaluator-facing artifact preserves the historical rejected
baseline and places current claim pages first. Raw JSON, independent checkers,
tamper tests, source hashes, seeds, runtimes, and limitations are linked from
each page.

---

Original workspace title:
`icml26-repro-tiF3tA5pau-continuous-variable-hamiltonian-learning-at-heisenberg-limit-via-displacemen`.
