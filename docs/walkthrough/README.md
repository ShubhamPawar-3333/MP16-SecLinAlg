# Code walkthrough — every line, in plain language

These documents explain the reference implementation in
[`../../seclinalg/`](../../seclinalg/) line by line, in simple language, for a
guide who needs to explain it to students (and for students reading ahead).

Read them in order — each layer builds on the one before:

| # | File | Covers | Backlog |
|---|------|--------|---------|
| 0 | this page | how the pieces fit together | — |
| 1 | [01-field.md](01-field.md) | `errors.py`, `field/primes.py`, `field/euclid.py`, `field/element.py` | FA-1, FA-2, FA-3 |
| 2 | [02-types.md](02-types.md) | `types/matrix.py`, `types/vector.py` | CT-1, CT-2, CT-3 |
| 3 | [03-linalg.md](03-linalg.md) | `linalg/multiply.py`, `elimination.py`, `analysis.py`, `solve.py` | LA-1..LA-5 |
| 4 | [04-sharing.md](04-sharing.md) | `sharing/shares.py` | SS-1..SS-4 |
| 5 | [05-secure.md](05-secure.md) | `secure/dealer.py`, `beaver.py`, `inner_product.py`, `mat_product.py` | SP-1..SP-3, VB-1 |

The matching list of mistakes students make is
[`../teaching/common-mistakes.md`](../teaching/common-mistakes.md).

---

## The whole library in one picture

```
        caller code  (tests, examples, a student's demo)
              │
     ┌────────┴─────────┐
     │                  │
  PLAINTEXT          SECURE
     │                  │
  Matrix / Vector    ShareSet
     │                  │
  linalg             secure
  (multiply,         (dealer, beaver_mul,
   elimination,       inner_product,
   analysis, solve)   mat_product)
     │                  │
     └────────┬─────────┘
              │
           sharing        ← share / reconstruct / local add
              │
            field         ← Field, FieldElement, modular inverse
              │
           errors.py      ← one exception hierarchy for everything
```

**The one rule that shapes everything:** a lower layer never imports an upper
layer. `field` knows nothing about matrices; `sharing` knows nothing about
`secure`. You can test each layer on its own.

## Two ideas that run through the whole codebase

### 1. Everything is exact, because everything is an integer mod p

There is no floating point below the type layer. A "number" in this library is a
`FieldElement`: an ordinary Python `int` kept in the range `0 .. p-1`, plus a
pointer to which prime `p` we are working mod. Addition, subtraction and
multiplication are the usual integer operations followed by `% p`. "Division"
is multiplication by a *modular inverse* (layer 1 explains this). Because it is
all integer arithmetic, `a == b` is either exactly true or exactly false — which
is what secret sharing needs.

### 2. Values are immutable; operations return new objects

`FieldElement`, `Matrix`, `Vector` and `ShareSet` never change themselves. `a + b`
builds and returns a **new** object; `a` and `b` are untouched. This means you
can pass the same matrix into two functions without one of them corrupting it
for the other. The only exception is `Matrix.__setitem__` (`m[i, j] = v`), which
the elimination algorithm uses on a private copy it made itself.

## Python features you will meet

| Feature | One-line explanation | First appears |
|---|---|---|
| `x % p` | remainder; in Python it is always `0..p-1` for positive `p`, even when `x` is negative | field |
| `isinstance(x, T)` | "is `x` a `T`?" — used to accept either an `int` or a `FieldElement` | field |
| dunder methods (`__add__`, `__eq__`, …) | let `a + b`, `a == b` work on our own types | field |
| `__slots__` | a small memory/typo optimisation: the object may only have the named attributes | field |
| `NotImplemented` | a method returns this to say "I don't know how to combine with that type"; Python then tries the other operand | field |
| `@property` | a method you call without `()` — `field.zero`, not `field.zero()` | field |
| `@dataclass` | auto-writes `__init__`/`__repr__`/`__eq__` for a plain data holder | linalg, sharing |
| generator (`yield`) | a function that produces values lazily, one at a time | types |
| list comprehension `[f(x) for x in xs]` | build a list in one line | everywhere |
