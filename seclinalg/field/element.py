"""Field and FieldElement  [W1]  (stories FA-1, FA-2, FA-3).

Field(p) validates that p is prime and is a factory for FieldElement. Every
element carries a reference to its field; operations across fields raise
FieldMismatch (SDD 8.1).
"""

from seclinalg.errors import FieldMismatch, NoInverse


class Field:
    """A prime field Z_p."""

    def __init__(self, p: int) -> None:
        raise NotImplementedError("FA-1: require_prime(p); cache zero/one")

    def element(self, x: int) -> "FieldElement":
        """Reduce x into [0, p) and wrap it."""
        raise NotImplementedError("FA-1")

    @property
    def zero(self) -> "FieldElement":
        raise NotImplementedError("FA-1")

    @property
    def one(self) -> "FieldElement":
        raise NotImplementedError("FA-1")

    def random(self) -> "FieldElement":
        """Uniform in [0, p), drawn with the `secrets` module (SDD 5.2)."""
        raise NotImplementedError("FA-1: secrets.randbelow(p)")


class FieldElement:
    """An element of a Field. Immutable; equality compares reduced values."""

    def __init__(self, value: int, field: Field) -> None:
        raise NotImplementedError("FA-1")

    def __add__(self, other): raise NotImplementedError("FA-1")
    def __sub__(self, other): raise NotImplementedError("FA-1")
    def __mul__(self, other): raise NotImplementedError("FA-1")
    def __neg__(self): raise NotImplementedError("FA-1")
    def __eq__(self, other): raise NotImplementedError("FA-1")
    def __hash__(self): raise NotImplementedError("FA-1")

    def inverse(self) -> "FieldElement":
        """self ** -1. Raise NoInverse for 0 (SDD 8.1)."""
        raise NotImplementedError("FA-2: field.mod_inverse")

    def __truediv__(self, other) -> "FieldElement":
        """self * other.inverse() -- defined, never a real division."""
        raise NotImplementedError("FA-2")
