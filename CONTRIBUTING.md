# Working agreement

- One shared repository. Small, frequent commits. Everyone can run `python -m pytest`.
- Each worklet owns its package directory. `seclinalg/errors.py` and the SDD 6
  interface contracts change only by agreement of all three teams.
- No `assert` in library code paths. No `None`/sentinel returns to signal failure
  — raise a typed error from `seclinalg.errors`.
- No floating point below the type layer. No `/` on field values — multiply by a
  modular inverse. CI greps for `float(` and bare `/` in `seclinalg/linalg/`.
- A tiny end-to-end example over `p = 101` (`examples/end_to_end.py`) must keep
  passing from week 1 onward.
- Every backlog story lands with its proving test (SDD 17 traceability).
