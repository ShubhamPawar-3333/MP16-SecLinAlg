# Layer 3 — linear algebra

Files: `seclinalg/linalg/multiply.py`, `seclinalg/linalg/elimination.py`,
`seclinalg/linalg/analysis.py`, `seclinalg/linalg/solve.py`.

`multiply` is a direct triple loop. Everything else in this layer is a thin read
of **one** function: `row_echelon`, which runs Gaussian elimination over the
field. Rank, determinant, inverse and solve all just call `row_echelon` and
interpret the result.

---

## `seclinalg/linalg/multiply.py`

```python
from seclinalg.errors import FieldMismatch, ShapeError
from seclinalg.types.matrix import Matrix
from seclinalg.types.vector import Vector
```

```python
def multiply(a: Matrix, b):
```
`b` is annotated loosely because it can be a `Matrix` or a `Vector`.

```python
    if isinstance(b, Vector):
        column = Matrix([[x] for x in b], a.field)
        product = multiply(a, column)
        return Vector([product[i, 0] for i in range(product.shape[0])], a.field)
```
If `b` is a vector, treat it as a one-column matrix (`[[x] for x in b]` makes
each entry its own row), multiply as matrices, then unwrap the single result
column back into a `Vector`. This is why `solve`'s tests can write
`multiply(A, x)`.

```python
    if a.field.p != b.field.p:
        raise FieldMismatch(f"Z_{a.field.p} matrix @ Z_{b.field.p} matrix")
    m, k = a.shape
    k2, p = b.shape
    if k != k2:
        raise ShapeError(f"cannot multiply {a.shape} by {b.shape}")
```
Same prime, and the inner dimensions must agree: an `m×k` times a `k×p`. `a`'s
column count `k` must equal `b`'s row count `k2`.

```python
    field = a.field
    ag, bg = a.to_grid(), b.to_grid()
```
Pull both matrices out as plain grids of elements — faster to index than going
through `__getitem__` repeatedly.

```python
    result = []
    for i in range(m):
        row = []
        for j in range(p):
            acc = field.zero
            for t in range(k):
                acc = acc + ag[i][t] * bg[t][j]
            row.append(acc)
        result.append(row)
    return Matrix(result, field)
```
The schoolbook triple loop. Result entry `(i, j)` is the dot product of row `i`
of A with column `j` of B: sum over `t` of `A[i][t] · B[t][j]`, starting from
`field.zero`. Every `+` and `*` is field arithmetic, so the result is exact.

**Cost.** The inner line runs `m · p · k` times: `m·k·p` multiplications and
`m·p·(k−1)` additions. For square `n` that is O(n³) — the number students should
be able to derive by counting these three loops. `benchmarks/matmul_bench.py`
shows the ~8× time growth per doubling of `n`.

---

## `seclinalg/linalg/elimination.py` — the heart of the layer

### The `EchelonResult` container

```python
from dataclasses import dataclass, field as _dc_field
```
`dataclass` auto-generates boilerplate (`__init__`, `__repr__`, `__eq__`) for a
plain data holder. We import `field` from `dataclasses` but rename it to
`_dc_field` so it does not clash with our own use of the word "field" (the
`Field` object).

```python
@dataclass
class EchelonResult:
    matrix: Matrix
    pivots: list = _dc_field(default_factory=list)
    swaps: int = 0
    pivot_values: list = _dc_field(default_factory=list)
```
Four pieces of output from elimination:
- `matrix` — the reduced row-echelon form (RREF), as a `Matrix`.
- `pivots` — the column index of each pivot, in increasing order. `[0, 1, 2]`
  means pivots in the first three columns.
- `swaps` — how many times two rows were exchanged (needed for the determinant
  sign).
- `pivot_values` — the **raw** pivot entry at each step, *before* it was
  normalised to 1 (needed to reconstruct the determinant).

`default_factory=list` means "if not supplied, start with a fresh empty list".
You cannot write `pivots: list = []` in a dataclass — that one list would be
shared between all instances, a classic Python trap.

```python
    @property
    def rank(self) -> int:
        return len(self.pivots)
```
Rank = number of pivots. A convenience so callers write `result.rank`.

### `row_echelon` — Gauss-Jordan over the field

```python
def row_echelon(a: Matrix) -> EchelonResult:
    field = a.field
    zero = field.zero
    g = a.to_grid()                     # list[list[FieldElement]], a private copy
    n_rows = len(g)
    n_cols = len(g[0])
```
Work on a **copy** (`to_grid`), so the caller's matrix is never modified. Cache
`zero` and the dimensions.

```python
    swaps = 0
    pivots: list[int] = []
    pivot_values: list = []
    pivot_row = 0
```
`pivot_row` is "the next row that will receive a pivot". It advances each time we
place one.

```python
    for col in range(n_cols):
```
Sweep the columns left to right. Each column either gets a pivot or is a "free"
column.

```python
        found = None
        for i in range(pivot_row, n_rows):
            if g[i][col] != zero:
                found = i
                break
```
Look for a non-zero entry in this column, at `pivot_row` or below. Take the
first one. **Any** non-zero entry works — over an exact field there is no
"choose the largest for stability" concern (there is not even an ordering on
field elements). This is a point students with a numerical-methods background
get wrong.

```python
        if found is None:
            continue                    # free column, move on
```
No pivot available in this column → it is a free column (a free variable, when
solving). Move to the next column *without* advancing `pivot_row`.

```python
        if found != pivot_row:
            g[pivot_row], g[found] = g[found], g[pivot_row]
            swaps += 1
```
If the non-zero entry is below `pivot_row`, swap that row up into position and
count the swap. Each swap flips the sign of the determinant, which is why we
count.

```python
        raw_pivot = g[pivot_row][col]
        pivots.append(col)
        pivot_values.append(raw_pivot)
```
Record the pivot's column, and its value *now*, before we scale it.

```python
        inv = raw_pivot.inverse()
        g[pivot_row] = [x * inv for x in g[pivot_row]]
```
Normalise: multiply the whole pivot row by the pivot's inverse, so the pivot
entry becomes 1. **This is the "never divide" rule.** `x / pivot` would be a
float; `x * pivot.inverse()` is exact field arithmetic (SDD 12.2).

```python
        for i in range(n_rows):
            if i != pivot_row and g[i][col] != zero:
                factor = g[i][col]
                g[i] = [xi - factor * xr for xi, xr in zip(g[i], g[pivot_row])]
```
Clear this column in **every other row** (that is what makes it *reduced* echelon
form, not just echelon form). For each other row, subtract `factor` copies of
the pivot row, where `factor` is that row's current entry in this column. After
this, column `col` is all zeros except the 1 at `pivot_row`.

```python
        pivot_row += 1
        if pivot_row == n_rows:
            break
```
Advance. If we have placed a pivot in every row, there is nothing left to do —
stop early.

```python
    return EchelonResult(Matrix(g, field), pivots, swaps, pivot_values)
```
Wrap the reduced grid back into a `Matrix` and return everything the derived
functions need.

**Worked example.** `[[0, 1], [1, 0]]`:
1. col 0: no non-zero at row 0; found at row 1 → swap → `swaps = 1`, grid is
   `[[1, 0], [0, 1]]`. Pivot value 1, normalise (no-op), clear column (already
   clear). `pivot_row = 1`.
2. col 1: non-zero at row 1 → pivot. Normalise (no-op), clear (already clear).
   `pivot_row = 2` → break.
Result: RREF = identity, `pivots = [0, 1]`, `swaps = 1`, `pivot_values = [1, 1]`.

---

## `seclinalg/linalg/analysis.py` — rank, determinant, inverse

```python
from seclinalg.errors import ShapeError, SingularMatrix
from seclinalg.linalg.elimination import row_echelon
from seclinalg.types.matrix import Matrix
```

```python
def rank(a: Matrix) -> int:
    return row_echelon(a).rank
```
Literally: reduce, count pivots. Works for any shape.

### `determinant`

```python
def determinant(a: Matrix):
    rows, cols = a.shape
    if rows != cols:
        raise ShapeError(f"determinant is defined only for a square matrix, got {a.shape}")
```
Determinant is only defined for square matrices.

```python
    result = row_echelon(a)
    if result.rank < rows:
        return a.field.zero                     # singular
```
If elimination found fewer pivots than rows, the matrix is rank-deficient and
its determinant is exactly 0.

```python
    acc = a.field.one
    for pivot_value in result.pivot_values:
        acc = acc * pivot_value
    return -acc if result.swaps % 2 else acc
```
Otherwise the determinant is the product of the **raw** pivots (the values before
normalisation — that is why `row_echelon` saved them), times `(-1)` for each row
swap. `result.swaps % 2` is 1 when the number of swaps is odd, so `-acc`;
0 (falsy) when even, so `acc`.

**Why raw pivots.** Elimination scaled each pivot row by `1/pivot`, which divides
the running determinant by that pivot. Multiplying the raw pivots back together
undoes exactly that. Compute from the *normalised* pivots (all 1) and you would
get determinant 1 for every invertible matrix — a real student bug.

### `inverse`

```python
def inverse(a: Matrix) -> Matrix:
    rows, cols = a.shape
    if rows != cols:
        raise ShapeError(f"only a square matrix has an inverse, got {a.shape}")

    n = rows
    augmented = a.hstack(Matrix.identity(n, a.field))
    result = row_echelon(augmented)
```
Build `[A | I]` (an `n × 2n` matrix) and reduce it. If `A` is invertible, the
left half becomes `I` and the right half becomes `A⁻¹` — the standard
Gauss-Jordan inversion.

```python
    if result.pivots != list(range(n)):
        raise SingularMatrix(f"matrix is not invertible (rank {result.rank} < {n})")
```
The left half is the identity **iff** the pivots are exactly columns
`0, 1, …, n-1`. If `A` is singular, elimination either finds fewer than `n`
pivots, or is forced to take a pivot in a right-half column (index ≥ n) — either
way `result.pivots != [0, 1, …, n-1]`, and we raise.

```python
    grid = result.matrix.to_grid()
    right_block = [row[n:] for row in grid]
    return Matrix(right_block, a.field)
```
Slice off the right half of every row (`row[n:]` = "from column n to the end")
and wrap it as a matrix. That is `A⁻¹`.

---

## `seclinalg/linalg/solve.py` — solve Ax = b

```python
from seclinalg.errors import InconsistentSystem, NoUniqueSolution, ShapeError
from seclinalg.linalg.elimination import row_echelon
from seclinalg.types.matrix import Matrix
from seclinalg.types.vector import Vector
```

### `_as_column` — accept b in whatever form

```python
def _as_column(b, field, expected_len: int) -> list:
    if isinstance(b, Vector):
        entries = list(b)
    elif isinstance(b, Matrix):
        if b.shape[1] != 1:
            raise ShapeError(f"right-hand side must be a column, got {b.shape}")
        entries = [b[i, 0] for i in range(b.shape[0])]
    else:
        entries = [field.element(x) for x in b]
```
`b` may be a `Vector`, an `n×1` `Matrix`, or a plain list. Normalise all three to
a Python list of entries. A `Matrix` with more than one column is rejected.

```python
    if len(entries) != expected_len:
        raise ShapeError(f"right-hand side has length {len(entries)}, expected {expected_len}")
    return [field.element(x) for x in entries]
```
Length must match the number of equations (`A`'s row count). Convert every entry
to a field element and return the list.

### `solve`

```python
def solve(a: Matrix, b) -> Vector:
    field = a.field
    zero = field.zero
    m, n = a.shape
    rhs = _as_column(b, field, m)
```
`m` equations, `n` unknowns. `rhs` is the right-hand side as a clean list.

```python
    augmented = a.hstack(Matrix([[x] for x in rhs], field))
    result = row_echelon(augmented)
    grid = result.matrix.to_grid()
```
Build `[A | b]` (`m × (n+1)`), reduce it, and pull the reduced grid.

```python
    for row in grid:
        if all(x == zero for x in row[:n]) and row[n] != zero:
            raise InconsistentSystem("system has no solution")
```
**Inconsistent check.** If any reduced row is all zeros across the `A` part
(`row[:n]` = the first `n` columns) but has a non-zero in the `b` column
(`row[n]`), that row says `0 = (something non-zero)` — impossible. No solution.

```python
    a_pivots = [c for c in result.pivots if c < n]
    if len(a_pivots) < n:
        free = n - len(a_pivots)
        raise NoUniqueSolution(f"system is under-determined ({free} free variable(s))")
```
**Uniqueness check.** Count pivots that fall inside the `A` block (column
`< n`). If there are fewer than `n`, some unknown has no pivot — it is a free
variable, so there are infinitely many solutions. This is a *different* outcome
from "no solution" and gets a different exception (LA-5 tests both).

```python
    x = [zero] * n
    for pivot_row, col in enumerate(a_pivots):
        x[col] = grid[pivot_row][n]
    return Vector(x, field)
```
**Unique case.** There are exactly `n` pivots, one per unknown. Because it is
*reduced* echelon form, pivot row `i` now reads `1 · x[col] = grid[i][n]`, so the
answer for that unknown is simply the entry in the `b` column of that row.
`enumerate` gives `(0, first pivot col), (1, second pivot col), …`. Collect the
values into `x` and return it as a `Vector`.

---

## How the pieces connect

```python
f = Field(101)
A = Matrix([[2, 1, 1], [1, 3, 2], [1, 0, 2]], f)

rank(A)                  # row_echelon -> 3 pivots -> 3
determinant(A)           # raw pivots multiplied, sign from swaps -> 9 (mod 101)
Ainv = inverse(A)        # reduce [A | I], take right half
multiply(A, Ainv)        # identity

b = multiply(A, Vector([4, 1, 3], f))   # b = [12, 13, 10]
solve(A, b)              # Vector[col 3 mod 101](4 1 3)

solve(Matrix([[1, 1]], f), [1])         # NoUniqueSolution  (1 eq, 2 unknowns)
solve(Matrix([[1, 1], [1, 1]], f), [1, 2])   # InconsistentSystem
```

Next: [`04-sharing.md`](04-sharing.md) — splitting a secret into shares that add
up to it.
