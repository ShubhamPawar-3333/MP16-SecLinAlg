# MP16 — Secure Linear Algebra Library

A foundations-first educational library: exact finite-field arithmetic, generic
Vector/Matrix types and algorithms, and additive secret-sharing primitives for
secure computation. Python standard library only.

- `docs/design/MP16-System-Design-Document.html` — the full design (HLD + LLD).
- `docs/walkthrough/` — every line of the reference code explained in plain language.
- `docs/teaching/common-mistakes.md` — mistakes students make, layer by layer, with the question to ask each time.
- `docs/security/` — threat model, the n−1 privacy proof, the multiplication boundary.

## Layout

| Path | Owner | Contents |
|------|-------|----------|
| `seclinalg/field/`   | W1 | `Field`, `FieldElement`, extended Euclid, primality |
| `seclinalg/types/`   | W1 | `Vector`, `Matrix`, core operations |
| `seclinalg/linalg/`  | W1 (multiply) / W2 | multiply, elimination, rank/det/inverse, solve |
| `seclinalg/sharing/` | W3 | `share`, `reconstruct`, `add_shares`, local ops |
| `seclinalg/secure/`  | W3 | trusted dealer, Beaver multiply, inner/matrix product |
| `seclinalg/errors.py`| shared | the `SecLinAlgError` hierarchy |

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .            # editable install; also `pip install pytest`

python -m pytest            # full suite (99 tests)
python -m pytest tests/field
python examples/end_to_end.py
python benchmarks/matmul_bench.py
```

The library itself has no dependencies; `pytest` is the only dev dependency.

## Status

All five layers are implemented and tested (FA, CT, LA-1..LA-5, SS, SP, VB-1).
Not yet done: LA-6 Strassen (Could), VB-2 as a committed artefact, and the
SP-4 boundary write-up polish. See `docs/design/decision-log.md`.

## Locked decisions (SDD 5.2)

- Python standard library only. No NumPy / BLAS / MP-SPDZ / floating point in core.
- Test prime `p = 101`; runtime prime `p = 2**31 - 1` (Mersenne).
- Default party count `n = 3`. Share randomness from the `secrets` module.
- Honest-but-curious threat model, single-process simulation.

## Worklets

Three teams work in parallel against the frozen interface contracts (SDD 6):
W1 field + types, W2 linear algebra, W3 secure computation.
