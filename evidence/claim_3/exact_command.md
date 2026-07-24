# Claim 3 exact command

```text
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

This inherited command cumulatively reruns the frozen historical regression
and the accepted Claim 6 and Claim 4 verifiers before Claim 3.

Pre-run compute estimate: one CPU core, explicitly thread-capped, expected
under five minutes. Selected backend: local CPU.
