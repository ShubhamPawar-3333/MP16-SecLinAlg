"""Matrix: row-major, bound to a field at construction  [W1]  (CT-1..CT-3).

Invariants (SDD 8.2):
  * construction validates the row list is rectangular and non-empty, else ShapeError
  * ``.shape`` -> (rows, cols)
  * ``add``, ``sub``, ``scalar_mul``, ``transpose`` never mutate an operand --
    each returns a fresh Matrix
  * ``__setitem__`` is the one mutating entry point, used when an algorithm builds
    a working copy of its own

Entries are stored as FieldElement. Callers may pass ints or FieldElements;
both are reduced into the field at construction.
"""

from seclinalg.errors import FieldMismatch, ShapeError


class Matrix:
    __slots__ = ("field", "_data")

    def __init__(self, rows, field) -> None:
        data = []
        width = None
        for r in rows:
            r = list(r)
            if width is None:
                width = len(r)
            elif len(r) != width:
                raise ShapeError(f"ragged rows: expected width {width}, got {len(r)}")
            data.append([field.element(x) for x in r])
        if not data or width == 0:
            raise ShapeError("a matrix needs at least one row and one column")
        self.field = field
        self._data = data

    # --- construction helpers ----------------------------------------------
    @classmethod
    def from_grid(cls, grid, field) -> "Matrix":
        return cls(grid, field)

    @staticmethod
    def identity(n: int, field) -> "Matrix":
        return Matrix([[1 if i == j else 0 for j in range(n)] for i in range(n)], field)

    @staticmethod
    def zeros(rows: int, cols: int, field) -> "Matrix":
        return Matrix([[0] * cols for _ in range(rows)], field)

    def copy(self) -> "Matrix":
        return Matrix(self.to_grid(), self.field)

    def to_grid(self) -> list:
        """A fresh list-of-lists of FieldElement -- the form the linalg
        algorithms work on."""
        return [list(row) for row in self._data]

    # --- shape / indexing ----------------------------------------------------
    @property
    def shape(self) -> tuple[int, int]:
        return (len(self._data), len(self._data[0]))

    def __getitem__(self, key):
        if isinstance(key, tuple):
            i, j = key
            return self._data[i][j]
        return list(self._data[key])          # a copy of row i

    def __setitem__(self, key, value) -> None:
        if not isinstance(key, tuple):
            raise TypeError("assign entries one at a time: m[i, j] = value")
        i, j = key
        self._data[i][j] = self.field.element(value)

    def __iter__(self):
        for row in self._data:
            yield list(row)

    def column(self, j: int) -> list:
        return [self._data[i][j] for i in range(self.shape[0])]

    # --- operations (all non-mutating) ------------------------------------
    def _require_same_shape(self, other: "Matrix") -> None:
        if not isinstance(other, Matrix):
            raise TypeError(f"expected Matrix, got {type(other).__name__}")
        if self.field.p != other.field.p:
            raise FieldMismatch(f"Z_{self.field.p} matrix with Z_{other.field.p} matrix")
        if self.shape != other.shape:
            raise ShapeError(f"shape mismatch: {self.shape} vs {other.shape}")

    def add(self, other: "Matrix") -> "Matrix":
        self._require_same_shape(other)
        return Matrix(
            [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(self._data, other._data)],
            self.field,
        )

    def sub(self, other: "Matrix") -> "Matrix":
        self._require_same_shape(other)
        return Matrix(
            [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(self._data, other._data)],
            self.field,
        )

    def scalar_mul(self, k) -> "Matrix":
        k = self.field.element(k)
        return Matrix([[k * a for a in row] for row in self._data], self.field)

    def transpose(self) -> "Matrix":
        rows, cols = self.shape
        return Matrix([[self._data[i][j] for i in range(rows)] for j in range(cols)], self.field)

    def hstack(self, other: "Matrix") -> "Matrix":
        """[ self | other ] -- used to build [A | I] and [A | b] for elimination."""
        if not isinstance(other, Matrix):
            raise TypeError(f"expected Matrix, got {type(other).__name__}")
        if self.field.p != other.field.p:
            raise FieldMismatch(f"Z_{self.field.p} matrix with Z_{other.field.p} matrix")
        if self.shape[0] != other.shape[0]:
            raise ShapeError(f"row-count mismatch: {self.shape[0]} vs {other.shape[0]}")
        return Matrix(
            [ra + rb for ra, rb in zip(self.to_grid(), other.to_grid())], self.field
        )

    # --- operator sugar ----------------------------------------------------
    __add__ = add
    __sub__ = sub

    def __neg__(self) -> "Matrix":
        return self.scalar_mul(-1)

    def __matmul__(self, other):
        from seclinalg.linalg.multiply import multiply

        return multiply(self, other)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Matrix):
            return NotImplemented
        return (
            self.field.p == other.field.p
            and self.shape == other.shape
            and self._data == other._data
        )

    def __repr__(self) -> str:
        body = "; ".join(" ".join(str(int(x)) for x in row) for row in self._data)
        return f"Matrix[{self.shape[0]}x{self.shape[1]} mod {self.field.p}]({body})"
