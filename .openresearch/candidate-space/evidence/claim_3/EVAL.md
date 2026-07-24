# Claim 3 evaluation

Status after formal run: `VERIFIED` under the exact Section 3.6 contract.

- Accepted run: `6d6f78f3-b9b5-4ed3-bbb3-15bd6da140fc`.
- Commit: `3f66f82603c3bb6b71e4afbc67abd40b2e3f9756`.
- Exit code: 0.
- OpenResearch wall duration: 25 seconds.
- Every predeclared acceptance check passed.
- Independent checker exited zero.
- The underestimated-constant control violated the bound as required.
- A tampered acceptance boolean made the checker exit one and identify the
  failed symbolic-gradient check.

The failed unpaired-direction predecessor is retained in
`attempt_1_failed.md`. The accepted child changed only the pairing design, not
the physical model, threshold, or acceptance interval.
