# Claim 3 attempt 1: rejected unpaired-direction slope

- Experiment: `1fc653d7-a1a3-4a86-bf74-d60cc85b211c`.
- Run: `9468caf8-78cb-4130-b90c-f665ac0a8a1b`.
- Commit: `0e7406b5a947ec25744eebf05e8aa752c68729d6`.
- Outcome: process exit 1; verdict `BLOCKED`.

All direct Claim 3 obligations passed: exact symbolic gradient, full-rank
Algorithm 1 design, derived `L_C`, finite-Fock D-RUT agreement, all 60
Equation (43) inequalities, and the underestimated-constant control. The
maximum bound ratio was `0.254153`.

The separately predeclared small-error slope was `0.927979`, below the
`[0.94,1.06]` interval. Each magnitude had been assigned a newly generated
set of directions, so direction-dependent amplification changed along with
scale. This is not a valid paired scaling design.

The child correction generates twelve seeded directions once and evaluates
every one at all five magnitudes. No threshold, domain, physical model, or
acceptance interval is changed.
