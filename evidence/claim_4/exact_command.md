# Claim 4 exact command

The fixed command inherited by every experiment node is:

```text
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

This command reruns the frozen historical regression, the accepted Claim 6
pipeline, and the Claim 4 verifier cumulatively.

Compute forecast before the formal run: one CPU core, thread-capped, expected
runtime below five minutes. Per the authorized compute policy, the selected
backend is local CPU.
