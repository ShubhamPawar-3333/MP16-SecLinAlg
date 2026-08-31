# Layer 2 — Vector and Matrix

Files: `seclinalg/types/matrix.py`, `seclinalg/types/vector.py`.

A `Matrix` is a rectangular grid of `FieldElement`s (layer 1) plus the field
they live in. A `Vector` is the 1-D case. Both are immutable in the sense that
their operations return new objects — the one exception is `Matrix[i, j] = v`,
which the elimination algorithm uses on a copy it owns.

---

## `seclinalg/types/matrix.py`

```python
from seclinalg.errors import FieldMismatch, ShapeError
```
The two errors this file raises: `FieldMismatch` (mixing two primes),
`ShapeError` (ragged rows, wrong dimensions).

```python
class Matrix:
    __slots__ = ("field", "_data")
```
Each matrix holds its `field` and `_data`, a list of rows where each row is a
list of `FieldElement`. `__slots__` locks it to those two attributes.

### Construction

```python
    def __init__(self, rows, field) -> None:
        data = []
        width = None
        for r in rows:
            r = list(r)
```
Walk the incoming rows. `r = list(r)` makes a fresh copy of each row — so if the
caller later mutates the list they passed in, our matrix is unaffected. It also
lets the caller pass any iterable (a tuple, a generator), not just a list.

```python
            if width is None:
                width = len(r)
            elif len(r) != width:
                raise ShapeError(f"ragged rows: expected width {width}, got {len(r)}")
```
The first row sets the expected width. Every later row must match, or the matrix
is not rectangular → `ShapeError`, raised **now**, at construction, not later in
some algorithm.

```python
            data.append([field.element(x) for x in r])
```
`[field.element(x) for x in r]` is a list comprehension: convert every entry of
the row into a `FieldElement` of this field. A caller can pass raw ints
(`[[1, 2], [3, 4]]`) or elements or a mix; they all come out as reduced elements.

```python
        if not data or width == 0:
            raise ShapeError("a matrix needs at least one row and one column")
        self.field = field
        self._data = data
```
`not data` is `True` for an empty list — reject a matrix with no rows.
`width == 0` rejects `[[], []]` (rows present but empty). Then store.

### Factory helpers

```python
    @classmethod
    def from_grid(cls, grid, field) -> "Matrix":
        return cls(grid, field)
```
A named alias for the constructor. `@classmethod` means `cls` is `Matrix`
itself. Reads well when a caller already has a list-of-lists: `Matrix.from_grid(g, f)`.

```python
    @staticmethod
    def identity(n: int, field) -> "Matrix":
        return Matrix([[1 if i == j else 0 for j in range(n)] for i in range(n)], field)
```
The n×n identity: 1 on the diagonal (`i == j`), 0 elsewhere. The nested
comprehension reads "for each row `i`, for each column `j`, put 1 if on the
diagonal else 0". `@staticmethod` — no `self` or `cls`, it is just a function
that lives on the class for tidiness.

```python
    @staticmethod
    def zeros(rows: int, cols: int, field) -> "Matrix":
        return Matrix([[0] * cols for _ in range(rows)], field)
```
An all-zero matrix. `[0] * cols` is a row of `cols` zeros; `for _ in range(rows)`
repeats it `rows` times. `_` means "loop variable I don't use".

```python
    def copy(self) -> "Matrix":
        return Matrix(self.to_grid(), self.field)
```
A deep-enough copy: `to_grid` (below) hands fresh row lists to a fresh matrix.

```python
    def to_grid(self) -> list:
        return [list(row) for row in self._data]
```
Return the contents as a plain list-of-lists of `FieldElement`, with **new** row
lists so the caller cannot reach back into `self._data`. This is the form the
`linalg` algorithms work on — they call `to_grid()`, mutate the copy freely, and
build a new `Matrix` from the result.

### Shape and indexing

```python
    @property
    def shape(self) -> tuple[int, int]:
        return (len(self._data), len(self._data[0]))
```
`m.shape` → `(rows, cols)`. Rows = number of row lists; cols = length of the
first row (all rows are equal length, guaranteed at construction).

```python
    def __getitem__(self, key):
        if isinstance(key, tuple):
            i, j = key
            return self._data[i][j]
        return list(self._data[key])          # a copy of row i
```
Makes `m[...]` work.
- `m[i, j]` — Python passes `key` as the tuple `(i, j)`; return that one element.
- `m[i]` — `key` is a plain int; return a **copy** of row `i`. The copy matters:
  `m[0][0] = 5` then changes a throwaway list, not the matrix. (To change the
  matrix you must use `m[0, 0] = 5`, next method.)

```python
    def __setitem__(self, key, value) -> None:
        if not isinstance(key, tuple):
            raise TypeError("assign entries one at a time: m[i, j] = value")
        i, j = key
        self._data[i][j] = self.field.element(value)
```
The one mutating operation. Only `m[i, j] = v` is allowed; `m[0] = [1, 2]` is
rejected so nobody accidentally replaces a whole row and dodges the rectangular
check. `value` is run through `field.element` so you can assign a raw int.

```python
    def __iter__(self):
        for row in self._data:
            yield list(row)
```
Makes `for row in matrix:` work. `yield` produces the rows one at a time
(a *generator*). Each yielded row is a copy, same protective reasoning as
`__getitem__`.

```python
    def column(self, j: int) -> list:
        return [self._data[i][j] for i in range(self.shape[0])]
```
Extract column `j` as a list. Used where an algorithm needs columns (matrix
multiply reads columns of the right operand).

### Operations — all return a new matrix

```python
    def _require_same_shape(self, other: "Matrix") -> None:
        if not isinstance(other, Matrix):
            raise TypeError(f"expected Matrix, got {type(other).__name__}")
        if self.field.p != other.field.p:
            raise FieldMismatch(f"Z_{self.field.p} matrix with Z_{other.field.p} matrix")
        if self.shape != other.shape:
            raise ShapeError(f"shape mismatch: {self.shape} vs {other.shape}")
```
Shared precondition check for `add`/`sub`: other must be a `Matrix`, same prime,
same shape. `type(other).__name__` gives the class name for a helpful message
(`"int"`, `"list"`).

```python
    def add(self, other: "Matrix") -> "Matrix":
        self._require_same_shape(other)
        return Matrix(
            [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(self._data, other._data)],
            self.field,
        )
```
Element-wise sum. `zip(self._data, other._data)` pairs row `ra` of self with row
`rb` of other; the inner `zip(ra, rb)` pairs the entries; `a + b` is field
addition (layer 1). A brand-new `Matrix` is built and returned — `self` and
`other` are untouched.

```python
    def sub(self, other: "Matrix") -> "Matrix":
        self._require_same_shape(other)
        return Matrix(
            [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(self._data, other._data)],
            self.field,
        )
```
Same, with subtraction.

```python
    def scalar_mul(self, k) -> "Matrix":
        k = self.field.element(k)
        return Matrix([[k * a for a in row] for row in self._data], self.field)
```
Multiply every entry by one field element `k` (a raw int is accepted and
converted). New matrix.

```python
    def transpose(self) -> "Matrix":
        rows, cols = self.shape
        return Matrix([[self._data[i][j] for i in range(rows)] for j in range(cols)], self.field)
```
Swap rows and columns: the new entry at `(j, i)` is the old entry at `(i, j)`.
The outer loop runs over `j` (new rows = old columns), the inner over `i`. New
matrix; the original is not modified (a mistake students make is transposing in
place and aliasing rows).

```python
    def hstack(self, other: "Matrix") -> "Matrix":
        if not isinstance(other, Matrix):
            raise TypeError(f"expected Matrix, got {type(other).__name__}")
        if self.field.p != other.field.p:
            raise FieldMismatch(f"Z_{self.field.p} matrix with Z_{other.field.p} matrix")
        if self.shape[0] != other.shape[0]:
            raise ShapeError(f"row-count mismatch: {self.shape[0]} vs {other.shape[0]}")
        return Matrix(
            [ra + rb for ra, rb in zip(self.to_grid(), other.to_grid())], self.field
        )
```
Glue two matrices side by side: `[ self | other ]`. Needs the same number of
rows. `ra + rb` here is *list* concatenation (row of self followed by row of
other), not field addition. This is how `analysis.inverse` builds `[A | I]` and
`solve` builds `[A | b]`.

### Operators

```python
    __add__ = add
    __sub__ = sub
```
So `A + B` and `A - B` call `add`/`sub`. (Assigning the method to the dunder
name is a compact way to give two spellings.)

```python
    def __neg__(self) -> "Matrix":
        return self.scalar_mul(-1)
```
`-A` is `A` scaled by −1.

```python
    def __matmul__(self, other):
        from seclinalg.linalg.multiply import multiply
        return multiply(self, other)
```
`A @ B` — Python's matrix-multiply operator. The import is *inside* the method,
not at the top of the file, to avoid a circular import: `linalg.multiply` imports
`Matrix`, so `Matrix` cannot import `linalg.multiply` at load time. Deferring it
to call time breaks the cycle.

```python
    def __eq__(self, other) -> bool:
        if not isinstance(other, Matrix):
            return NotImplemented
        return (
            self.field.p == other.field.p
            and self.shape == other.shape
            and self._data == other._data
        )
```
Two matrices are equal iff same prime, same shape, same entries. `self._data ==
other._data` compares list-of-lists element by element, and each element
comparison is `FieldElement.__eq__` from layer 1. Guarding on `self.field.p ==
other.field.p` first means we never trigger a cross-prime `FieldMismatch` here.

```python
    def __repr__(self) -> str:
        body = "; ".join(" ".join(str(int(x)) for x in row) for row in self._data)
        return f"Matrix[{self.shape[0]}x{self.shape[1]} mod {self.field.p}]({body})"
```
Readable printout, e.g. `Matrix[2x2 mod 101](19 22; 43 50)`. `str(int(x))` turns
each element into its bare number; spaces separate a row; `; ` separates rows.

---

## `seclinalg/types/vector.py`

Deliberately minimal — a vector is a list of elements plus an orientation flag.

```python
class Vector:
    __slots__ = ("field", "_data", "column")
```
`column` is `True` for a column vector, `False` for a row vector. It only
matters for equality and printing here; the linear-algebra layer mostly works
with matrices.

```python
    def __init__(self, entries, field, column: bool = True) -> None:
        data = [field.element(x) for x in entries]
        if not data:
            raise ShapeError("a vector needs at least one entry")
        self.field = field
        self._data = data
        self.column = column
```
Convert every entry to a `FieldElement`; reject the empty vector; store. `column`
defaults to `True`.

```python
    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, i):
        return self._data[i]

    def __iter__(self):
        return iter(self._data)
```
`len(v)`, `v[i]`, and `for x in v:` all work. `__getitem__` returns the element
directly (elements are immutable, so no defensive copy is needed for a single
one).

```python
    def _require_match(self, other: "Vector") -> None:
        if not isinstance(other, Vector):
            raise TypeError(f"expected Vector, got {type(other).__name__}")
        if self.field.p != other.field.p:
            raise FieldMismatch(f"Z_{self.field.p} vector with Z_{other.field.p} vector")
        if len(self) != len(other):
            raise ShapeError(f"length mismatch: {len(self)} vs {len(other)}")
```
Same-shape / same-field check for the binary operations.

```python
    def add(self, other: "Vector") -> "Vector":
        self._require_match(other)
        return Vector([a + b for a, b in zip(self._data, other._data)], self.field, self.column)

    def sub(self, other: "Vector") -> "Vector":
        self._require_match(other)
        return Vector([a - b for a, b in zip(self._data, other._data)], self.field, self.column)

    def scalar_mul(self, k) -> "Vector":
        k = self.field.element(k)
        return Vector([k * a for a in self._data], self.field, self.column)
```
Element-wise add / subtract / scale, each returning a new vector that keeps the
same orientation.

```python
    def dot(self, other: "Vector"):
        self._require_match(other)
        acc = self.field.zero
        for a, b in zip(self._data, other._data):
            acc = acc + a * b
        return acc
```
The plaintext inner product: sum of `a·b` over the pairs, starting from the
field's zero. Returns one `FieldElement`. The **private** version of this — where
the two vectors are secret-shared — is in layer 5; this one is the reference the
tests compare against.

```python
    __add__ = add
    __sub__ = sub

    def __neg__(self) -> "Vector":
        return self.scalar_mul(-1)
```
Operator spellings.

```python
    def __eq__(self, other) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return (
            self.field.p == other.field.p
            and self.column == other.column
            and self._data == other._data
        )
```
Equal iff same prime, same orientation, same entries. Note a column vector and a
row vector with identical entries are **not** equal — orientation is part of the
identity.

```python
    def __repr__(self) -> str:
        kind = "col" if self.column else "row"
        return f"Vector[{kind} {len(self)} mod {self.field.p}]({' '.join(str(int(x)) for x in self._data)})"
```
E.g. `Vector[col 3 mod 101](4 1 3)`.

---

## How the pieces connect

```python
f = Field(101)
A = Matrix([[1, 2], [3, 4]], f)
I = Matrix.identity(2, f)
A + I                     # Matrix[2x2 mod 101](2 2; 3 5)
A.transpose()            # Matrix[2x2 mod 101](1 3; 2 4)
A.scalar_mul(50)         # every entry * 50 mod 101
A.hstack(I)              # Matrix[2x4 mod 101](1 2 1 0; 3 4 0 1)   <- [A | I]

v = Vector([5, 6], f)
w = Vector([7, 8], f)
v.dot(w)                 # 5*7 + 6*8 = 83  ->  83 (mod 101)
```

Next: [`03-linalg.md`](03-linalg.md) — multiply, then Gaussian elimination and
everything read off it.
