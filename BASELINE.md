# Historical judged baseline

This root preserves the evaluator-visible proxy implementation judged at
Hugging Face Space revision
`DineshAI/tiF3tA5pau@546ee65587074c6e5d2c46efeec0a87abc49048f`.

No author implementation or paper code repository was discoverable from
arXiv:2510.08419, alphaXiv, the paper text, or a targeted web search. The
published Space exposed `repro/src/verify_drut.py` but not its imported helper
module, so `repro/src/drut.py` below is a minimal reconstruction of the standard
linear-algebra helpers required to reproduce the displayed historical output.

This is intentionally a historical control, not faithful D-RUT evidence. It
does not implement bosonic Fock-space dynamics, displacements, random-unitary
twirling, robust phase estimation, or the first-quantization Bogoliubov search.
The live judge correctly classified five claims as TOY and one as
INCONCLUSIVE.

Fixed command:

```bash
uv sync --frozen --no-dev && uv run --frozen python repro/src/verify_drut.py
```

The root is frozen after its first completed run. All scientific changes belong
on descendant experiment branches.
