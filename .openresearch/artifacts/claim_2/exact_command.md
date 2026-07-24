# Fixed command

```bash
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

The repository-level `pyproject.toml`, `uv.lock`, and single `.venv` define
the environment. The entrypoint caps numerical libraries to one thread.
