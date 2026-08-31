# Decision log

Append-only. One row per decision, newest at the bottom.

| Date | Decision | Rationale | Reference |
|------|----------|-----------|-----------|
| 2026-08 | Python standard library only | foundations-first; no hidden BLAS | SDD 5.2 |
| 2026-08 | Test prime p = 101, runtime prime p = 2**31 - 1 | small p is hand-checkable; Mersenne is fast | SDD 5.2 |
| 2026-08 | Default party count n = 3 | smallest n that shows n-1 privacy | SDD 5.2 |
| 2026-08 | Share randomness from `secrets` | not `random`; cryptographic quality | SDD 5.2 |
| _open_ | Explicit party objects in the demo vs. one object | stronger viva if explicit | SDD 18 |
| _open_ | Strassen (LA-6) in or out for this team | time budget vs. secure layer | SDD 18 |
