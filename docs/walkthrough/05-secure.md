# Layer 5 — secure computation

Files: `seclinalg/secure/dealer.py`, `seclinalg/secure/beaver.py`,
`seclinalg/secure/inner_product.py`, `seclinalg/secure/mat_product.py`.

Layer 4 gave us **addition** of shared values for free. The missing piece is
**multiplication** of two shared values — `[x] · [y]` where neither `x` nor `y`
may be revealed. That needs one pre-shared random gadget per multiplication: a
**Beaver triple**.

---

## The Beaver trick, in words

A Beaver triple is three shared values `([a], [b], [c])` where `a` and `b` are
random and `c = a · b`. Someone trustworthy prepares these *ahead of time*,
before anyone knows `x` or `y`.

To multiply `[x]` by `[y]`:

1. Locally compute `[d] = [x] − [a]` and `[e] = [y] − [b]`. (Addition is free.)
2. **Open** `d` and `e` — reconstruct them in the clear. This is safe: `a` is
   random and secret, so `d = x − a` is `x` masked by a random pad — it looks
   like a uniformly random number and tells you nothing about `x`. Same for `e`.
3. Locally compute `[xy] = [c] + d·[b] + e·[a] + d·e`.

Only `d`, `e`, and the final answer are ever revealed. `x` and `y` stay hidden.

**Why step 3 works** (reconstruct both sides):
```
    c + d·b + e·a + d·e
  = ab + (x−a)·b + (y−b)·a + (x−a)·(y−b)      [substitute c=ab, d=x−a, e=y−b]
  = ab + xb − ab + ya − ba + xy − xb − ay + ab
  = xy
```
Every other term cancels. This derivation is a standard viva question.

---

## `seclinalg/secure/dealer.py` — where triples come from

```python
from dataclasses import dataclass
from seclinalg.errors import TripleExhausted
from seclinalg.sharing import ShareSet, share
```

```python
@dataclass(frozen=True)
class BeaverTriple:
    a: ShareSet
    b: ShareSet
    c: ShareSet
```
Just a named bundle of three share sets. `frozen=True` — immutable.

```python
class Dealer:
    def __init__(self, field, n: int, pool_size: int | None = None) -> None:
        self.field = field
        self.n = n
        self._issued = 0
        self._pool = (
            [self._make_triple() for _ in range(pool_size)]
            if pool_size is not None
            else None
        )
```
The dealer knows the field and the party count. `_issued` counts how many triples
it has handed out (handy for tests: "did this matrix product really use m·k·p
triples?"). `pool_size`:
- `None` (default) → generate triples on demand, forever.
- a number → pre-generate exactly that many now; run out later and it raises.

The `X if cond else Y` on the right of `=` is a *conditional expression* — a
one-line if/else that produces a value.

```python
    def _make_triple(self) -> BeaverTriple:
        a = self.field.random()
        b = self.field.random()
        c = a * b
        return BeaverTriple(share(a, self.n), share(b, self.n), share(c, self.n))
```
Pick two random field elements, multiply them, and secret-share all three among
`n` parties. The parties end up holding `[a]`, `[b]`, `[c]` without any single
party knowing `a`, `b`, or `c`.

```python
    def next_triple(self) -> BeaverTriple:
        if self._pool is not None:
            if not self._pool:
                raise TripleExhausted(f"all {self._issued} pooled triples used")
            self._issued += 1
            return self._pool.pop()
        self._issued += 1
        return self._make_triple()
```
Hand out one triple. If there is a fixed pool: raise `TripleExhausted` when it is
empty, otherwise `pop()` one off. If there is no pool: make a fresh one. Either
way, bump `_issued`.

```python
    @property
    def issued(self) -> int:
        return self._issued
```
Read-only view of the counter.

**The honest bit:** this `Dealer` is a *simplification*. A real MPC system has no
trusted party — the participants generate triples among themselves with more
protocol machinery. Saying this out loud is required by story SP-4.

---

## `seclinalg/secure/beaver.py` — one shared×shared multiply

```python
from seclinalg.sharing import (
    ShareSet, add_public, add_shares, reconstruct, scalar_mul_shares, sub_shares,
)
```
Everything it needs is a *local* share operation from layer 4, plus
`reconstruct` for the two opens.

```python
def beaver_mul(x_shares: ShareSet, y_shares: ShareSet, triple) -> ShareSet:
    a, b, c = triple.a, triple.b, triple.c
```
Unpack `[a]`, `[b]`, `[c]`.

```python
    d = reconstruct(sub_shares(x_shares, a))      # open the mask x - a
    e = reconstruct(sub_shares(y_shares, b))      # open the mask y - b
```
Step 1 + 2: form `[x] − [a]` and `[y] − [b]` locally (`sub_shares`), then open
them. `d` and `e` are now public `FieldElement`s. This is the *only* place a
value derived from `x` or `y` is revealed — and it is safe because `a`, `b` are
random pads.

```python
    out = add_shares(c, scalar_mul_shares(d, b))
```
Start the recombination: `[c] + d·[b]`. `scalar_mul_shares(d, b)` scales the
shared `b` by the public `d`; `add_shares` adds it to `[c]`.

```python
    out = add_shares(out, scalar_mul_shares(e, a))
```
Add `e·[a]`.

```python
    out = add_public(d * e, out)
    return out
```
Add the public constant `d·e` (a plain field multiplication of two public
numbers) onto **one** share, via `add_public`. Return the resulting sharing of
`x·y`.

Note every step after the two opens is a layer-4 local operation — no more
communication, no more reveals.

---

## `seclinalg/secure/inner_product.py` — private dot product (SP-2)

```python
from seclinalg.errors import ShapeError
from seclinalg.sharing import ShareSet, add_shares, share
from seclinalg.secure.beaver import beaver_mul
```

```python
def private_inner_product(x_shares, y_shares, dealer) -> ShareSet:
    x_shares = list(x_shares)
    y_shares = list(y_shares)
    if len(x_shares) != len(y_shares):
        raise ShapeError(f"length mismatch: {len(x_shares)} vs {len(y_shares)}")
    if not x_shares:
        raise ShapeError("inner product of empty vectors")
```
`x_shares` and `y_shares` are lists of `ShareSet` — coordinate `i` of each vector
is shared separately. Check the lengths match and are non-zero.

```python
    n = x_shares[0].n
    field = x_shares[0].field
    acc = share(field.zero, n)                       # sharing of 0 -- neutral
```
The accumulator must itself be a **sharing** (of zero), not the integer `0` — we
are going to `add_shares` into it. A fresh sharing of zero adds nothing to the
secret.

```python
    for xs, ys in zip(x_shares, y_shares):
        term = beaver_mul(xs, ys, dealer.next_triple())
        acc = add_shares(acc, term)
    return acc
```
For each coordinate: multiply the two shared values with **one fresh Beaver
triple** (`dealer.next_triple()`), then add the shared product into the
accumulator. After the loop, `acc` is a sharing of `Σ xᵢ·yᵢ`. Cost: one triple
per coordinate, so a length-`k` inner product uses `k` triples.

**One triple per multiplication** matters: reusing a triple correlates the masks
`d`, `e` across products and starts to leak.

---

## `seclinalg/secure/mat_product.py` — private matrix product (SP-3)

```python
from seclinalg.errors import ShapeError
from seclinalg.secure.inner_product import private_inner_product
```

```python
def private_matrix_product(a_grid, b_grid, dealer) -> list:
    a_grid = [list(row) for row in a_grid]
    b_grid = [list(row) for row in b_grid]
```
Inputs are *grids* of `ShareSet` — `a_grid[i][t]` is the shared entry `A[i][t]`.
Using grids rather than the `Matrix` type keeps this module independent of
layer 2. Copy the rows defensively.

```python
    m = len(a_grid)
    k = len(a_grid[0])
    if len(b_grid) != k:
        raise ShapeError(f"cannot multiply {m}x{k} by {len(b_grid)}x{len(b_grid[0])}")
    p = len(b_grid[0])
```
`A` is `m×k`, `B` is `k×p`; inner dimensions must match.

```python
    b_cols = [[b_grid[t][j] for t in range(k)] for j in range(p)]
```
Pre-extract the columns of `B`: `b_cols[j]` is column `j` as a list of `k`
`ShareSet`s. This makes the main loop a clean "row dot column".

```python
    result = []
    for i in range(m):
        row = [private_inner_product(a_grid[i], b_cols[j], dealer) for j in range(p)]
        result.append(row)
    return result
```
Result entry `(i, j)` is the private inner product of row `i` of `A` with column
`j` of `B`. Each inner product uses `k` triples, and there are `m·p` of them, so
the whole matrix product consumes **m·k·p** triples — the number `Dealer.issued`
should show, and a good thing to have students predict before running.

The return is an `m×p` grid of `ShareSet`; the caller reconstructs each cell to
see the answer (see `examples/end_to_end.py`).

---

## How the pieces connect

```python
f = Field(101)
dealer = Dealer(f, n=3)

# one multiply
x, y = share(f.element(6), 3), share(f.element(7), 3)
reconstruct(beaver_mul(x, y, dealer.next_triple()))          # 42, dealer.issued == 1

# inner product of (1,2,3)·(4,5,6) = 32
xs = share_many([f.element(v) for v in (1, 2, 3)], 3)
ys = share_many([f.element(v) for v in (4, 5, 6)], 3)
reconstruct(private_inner_product(xs, ys, dealer))           # 32, +3 triples

# matrix product, checked against the plaintext one
A = Matrix([[1, 2], [3, 4]], f); B = Matrix([[5, 6], [7, 8]], f)
grid = lambda M: [[share(M[i, j], 3) for j in range(M.shape[1])] for i in range(M.shape[0])]
out = private_matrix_product(grid(A), grid(B), Dealer(f, 3))
Matrix([[int(reconstruct(c)) for c in row] for row in out], f) == multiply(A, B)   # True
```

That is the whole library: exact field arithmetic → matrices and elimination →
secret sharing → secure products, each layer only using the one below it.
