"""Matrix: row-major, bound to a field at construction  [W1]  (CT-1..CT-3).

Invariants (SDD 8.2):
    - construction validates the row list is rectangular, else ShapeError
    - .shape -> (rows, cols)
    - operations never mutate operands
"""

from seclinalg.errors import ShapeError


class Matrix:
    def __init__(self, rows, field) -> None:
        raise NotImplementedError("CT-1: validate rectangular; store field")

    @property
    def shape(self) -> tuple[int, int]:
        raise NotImplementedError("CT-1")

    def __getitem__(self, index): raise NotImplementedError("CT-1: bounds-checked")
    def __setitem__(self, index, value): raise NotImplementedError("CT-1")

    def add(self, other) -> "Matrix":
        """Require matching shape, else ShapeError (CT-2)."""
        raise NotImplementedError("CT-2")

    def sub(self, other) -> "Matrix":
        raise NotImplementedError("CT-2")

    def scalar_mul(self, k) -> "Matrix":
        """Multiply every entry by a field element (CT-2)."""
        raise NotImplementedError("CT-2")

    def transpose(self) -> "Matrix":
        """New matrix; does not mutate self (CT-2)."""
        raise NotImplementedError("CT-2")

    def __eq__(self, other) -> bool:
        """Compare field, shape, and all reduced entries (CT-2)."""
        raise NotImplementedError("CT-2")

    @staticmethod
    def identity(n: int, field) -> "Matrix":
        raise NotImplementedError("CT-1")
