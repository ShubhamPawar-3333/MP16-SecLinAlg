"""Vector: the 1-D case, with an orientation flag  [W1]  (CT-1, CT-2).

Kept deliberately small -- it reuses field arithmetic directly. ``dot`` is the
plaintext inner product; the *private* inner product lives in seclinalg.secure.
"""

from seclinalg.errors import FieldMismatch, ShapeError


class Vector:
    __slots__ = ("field", "_data", "column")

    def __init__(self, entries, field, column: bool = True) -> None:
        data = [field.element(x) for x in entries]
        if not data:
            raise ShapeError("a vector needs at least one entry")
        self.field = field
        self._data = data
        self.column = column

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, i):
        return self._data[i]

    def __iter__(self):
        return iter(self._data)

    def _require_match(self, other: "Vector") -> None:
        if not isinstance(other, Vector):
            raise TypeError(f"expected Vector, got {type(other).__name__}")
        if self.field.p != other.field.p:
            raise FieldMismatch(f"Z_{self.field.p} vector with Z_{other.field.p} vector")
        if len(self) != len(other):
            raise ShapeError(f"length mismatch: {len(self)} vs {len(other)}")

    def add(self, other: "Vector") -> "Vector":
        self._require_match(other)
        return Vector([a + b for a, b in zip(self._data, other._data)], self.field, self.column)

    def sub(self, other: "Vector") -> "Vector":
        self._require_match(other)
        return Vector([a - b for a, b in zip(self._data, other._data)], self.field, self.column)

    def scalar_mul(self, k) -> "Vector":
        k = self.field.element(k)
        return Vector([k * a for a in self._data], self.field, self.column)

    def dot(self, other: "Vector"):
        """Plaintext inner product -> FieldElement."""
        self._require_match(other)
        acc = self.field.zero
        for a, b in zip(self._data, other._data):
            acc = acc + a * b
        return acc

    __add__ = add
    __sub__ = sub

    def __neg__(self) -> "Vector":
        return self.scalar_mul(-1)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return (
            self.field.p == other.field.p
            and self.column == other.column
            and self._data == other._data
        )

    def __repr__(self) -> str:
        kind = "col" if self.column else "row"
        return f"Vector[{kind} {len(self)} mod {self.field.p}]({' '.join(str(int(x)) for x in self._data)})"
