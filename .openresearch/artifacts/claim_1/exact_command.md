# Fixed execution contract

```bash
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

The command is inherited unchanged by every experiment node. Dependencies are
pinned in repository-level `pyproject.toml` and `uv.lock`; execution uses the
single repository `.venv`. Numerical thread environment variables are capped
to one in the entrypoint.
