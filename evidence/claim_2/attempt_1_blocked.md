# Claim 2 attempt 1 — blocked calibration

Run `ef8ad2b3-8275-4a6f-acfb-ffb3c2acc4e6` at commit
`3f4f076` preserved the predeclared gates and returned `BLOCKED`.

- The `0.0025` validation achieved 30/32 successes, but its Wilson 95% lower
  bound was `0.798525`, just below the fixed `0.80` threshold.
- Three coarse targets selected the minimum candidate horizon. That saturation
  produced normalized resource slope `0.696219`, below the fixed `0.75`.

This second route changes the scientific design rather than relaxing gates:
it moves to five finer precisions and requires a calibration safety margin
(16/16 success and median RMSE at most target/3) before disjoint validation.
