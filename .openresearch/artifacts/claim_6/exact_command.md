# Exact command and locked environment

Inherited experiment command:

```bash
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

The root lock fixes CPython 3.12 and exact versions including NumPy 2.2.6,
SciPy 1.15.3, SymPy 1.14.0, and Matplotlib 3.10.3. The verifier sets BLAS and
OpenMP thread counts to one before importing NumPy.

Planned compute for this short verifier:

- Estimated cores: 1.
- Expected runtime: less than five minutes.
- Selected backend: local.
- Selected flavor: local backend has no reservable flavor.
- Actual allocation and runtime: recorded from `orx` after execution.
