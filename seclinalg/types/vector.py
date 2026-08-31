"""Vector: the 1-D case, with an orientation flag  [W1]  (CT-1, CT-2)."""

from seclinalg.errors import ShapeError


class Vector:
    def __init__(self, entries, field, column: bool = True) -> None:
        raise NotImplementedError("CT-1")

    def __len__(self) -> int:
        raise NotImplementedError("CT-1")

    def __getitem__(self, index): raise NotImplementedError("CT-1")

    def add(self, other) -> "Vector": raise NotImplementedError("CT-2")
    def sub(self, other) -> "Vector": raise NotImplementedError("CT-2")
    def scalar_mul(self, k) -> "Vector": raise NotImplementedError("CT-2")
    def __eq__(self, other) -> bool: raise NotImplementedError("CT-2")
