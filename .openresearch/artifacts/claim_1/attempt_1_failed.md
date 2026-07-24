# Claim 1 attempt 1 — evidence serialization failure

OpenResearch run `760b5856-7c06-49c5-af2f-ab0592e04bf4` at commit
`d6958a3c239abcad3a485f68dfb28d5871a1e1c4` ran the complete cumulative
workload for 40 seconds, then exited one before printing Claim 1 evidence.

Cause: an acceptance comparison produced a NumPy `bool_`, which Python's
standard JSON encoder does not serialize automatically. The correction only
normalizes NumPy scalar values to built-in JSON scalar types after all
computations. No design, seed, horizon, threshold, or scientific calculation
changed. This run supplies no Claim 1 verdict.
