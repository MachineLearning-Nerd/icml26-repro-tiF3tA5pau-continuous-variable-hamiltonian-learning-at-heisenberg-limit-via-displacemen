# Evaluator-blind pre-publication review

Review scope was restricted to the downloaded candidate tree and started only
from `pages/index.md`; no OpenResearch logs, branches, or repository knowledge
were used.

The reviewer opened, in order: `pages/index.md`, all six current claim pages,
`pages/visibility-matrix/page.md`, each linked claim contract, source audit,
raw JSON, checker output, negative-control output, tamper output, exact
command, environment lock, and limitations, then this release report.

First pass found Claims 1 and 2 missing from navigation and the visibility
matrix. Those gaps were fixed by adding current pages and all linked evidence.
The review was repeated after the fix.

Second-pass conclusion: every claim’s exact statement and source quantifiers,
assumption audit, executable source, fixed command, pinned environment, inline
numbers, raw downloadable data, checker, intended-failure control, tamper
exit, Git SHA, seed, CPU/runtime, and limitations were discoverable. Historical
pages were still reachable and labeled exactly `Historical rejected baseline`.
No conclusion required an unpublished path. Reviewer verdict: **visibility
gate passed for all six claims**.
