# Pre-publication gate results

- Candidate traversal began at `pages/index.md`.
- All six visibility-matrix rows have every required cell.
- Every JSON file parsed successfully.
- Every claim page exposed command, environment, raw JSON, checker, negative
  control, tamper result, Git SHA, seed, compute, and limitations.
- All 17 files in judged revision
  `546ee65587074c6e5d2c46efeec0a87abc49048f` are present in the candidate;
  historical missing count: `0`.
- Historical pages remain reachable and labeled `Historical rejected baseline`.
- All per-claim SHA-256 evidence manifests verified.
- The exact upload allowlist contains text files only.
- Credential-pattern scan returned no matches.
- `logbook.json` and every raw/checker/control JSON parsed.
- `marimo check notebooks/drut_tutorial.py` passed.
- Five report PNGs were generated at 1152-by-672 and the headline figure was
  visually inspected.
- Evaluator-blind second pass found no missing evidence.

Release gates pass subject to a final cumulative run of this release-candidate
commit and post-upload hash/traversal verification.
