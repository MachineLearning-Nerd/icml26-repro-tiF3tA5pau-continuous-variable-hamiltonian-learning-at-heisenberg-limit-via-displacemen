# Claim 5 exact command

```text
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

This fixed inherited command reruns all accepted Claim 6, Claim 4, and Claim 3
checks before Claim 5.

Pre-run compute estimate: one CPU core, thread-capped, expected under five
minutes. Selected backend: local CPU.
