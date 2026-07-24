# Claim 6 evaluation

Status after formal run: `VERIFIED` within the predeclared Claim 6 contract.

- Run: `bbf94f9d-627f-4af6-9d56-88baeb6004b5`.
- Commit: `90cbb933ed2d4d8775b78185823412a8536bcbf0`.
- Exit code: 0.
- OpenResearch wall duration: 20 seconds.
- Every predeclared acceptance check passed.
- Independent checker exited zero.
- Both negative controls failed for the intended physical reason.
- A tampered copy with one acceptance boolean forced false made the independent
  checker exit nonzero and name the failed check.

The exact Algorithm 1 chain was executed on a deterministic single-mode,
degree-2 Hamiltonian in a 24-state Fock truncation. This verdict is intentionally
limited to Claim 6 and does not imply verification of the universal scaling
claims.
