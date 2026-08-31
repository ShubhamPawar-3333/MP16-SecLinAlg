"""Field and FieldElement  [W1]  (stories FA-1, FA-2, FA-3).

Field(p) validates that p is prime and is a factory for FieldElement. Every
element carries a reference to its field; an operation between elements of two
different fields raises FieldMismatch (SDD 8.1).

Design notes for the students:
  * FieldElement is immutable -- there is no in-place arithmetic. Every operation
    returns a fresh element, so shared references can never be mutated out from
    under a caller.
  * Plain ints are accepted as the other operand (e.g. ``x + 1``) and are reduced
    into the field first. This keeps the matrix and sharing code readable. Two
    FieldElements from different primes never mix.
  * Division is defined as multiply-by-inverse. There is deliberately no path
    that performs a real ``/`` on field values (SDD 12.2).
"""

import secrets

from seclinalg.errors import FieldMismatch, NoInverse
from seclinalg.field.euclid import mod_inverse
from seclinalg.field.primes import require_prime


class Field:
    """The prime field Z_p."""

    __slots__ = ("p", "_zero", "_one")

    def __init__(self, p: int) -> None:
        self.p = require_prime(p)
        self._zero = FieldElement(0, self)
        self._one = FieldElement(1, self)

    def element(self, x) -> "FieldElement":
        """Reduce x into [0, p) and wrap it. An existing FieldElement is
        returned as-is when it belongs to this field, else FieldMismatch."""
        if isinstance(x, FieldElement):
            if x.field.p != self.p:
                raise FieldMismatch(f"element of Z_{x.field.p} used with Z_{self.p}")
            return x
        return FieldElement(int(x), self)

    @property
    def zero(self) -> "FieldElement":
        return self._zero

    @property
    def one(self) -> "FieldElement":
        return self._one

    def random(self) -> "FieldElement":
        """Uniform in [0, p). Uses `secrets`, not `random` -- share randomness
        must be cryptographic quality (SDD 5.2)."""
        return FieldElement(secrets.randbelow(self.p), self)

    def __eq__(self, other) -> bool:
        return isinstance(other, Field) and self.p == other.p

    def __hash__(self) -> int:
        return hash(("Field", self.p))

    def __repr__(self) -> str:
        return f"Field({self.p})"


class FieldElement:
    """An element of a Field. Immutable; equality compares reduced values."""

    __slots__ = ("value", "field")

    def __init__(self, value: int, field: Field) -> None:
        object.__setattr__(self, "value", value % field.p)
        object.__setattr__(self, "field", field)

    # --- immutability -----------------------------------------------------
    def __setattr__(self, name, value):
        raise AttributeError("FieldElement is immutable")

    def __delattr__(self, name):
        raise AttributeError("FieldElement is immutable")

    # --- operand handling ------------------------------------------------
    def _value_of(self, other):
        """Reduced int for `other`, or None if it is not a compatible operand.
        Raises FieldMismatch for a FieldElement from a different prime."""
        if isinstance(other, FieldElement):
            if other.field.p != self.field.p:
                raise FieldMismatch(f"Z_{self.field.p} operand with Z_{other.field.p} operand")
            return other.value
        if isinstance(other, int) and not isinstance(other, bool):
            return other % self.field.p
        return None

    def _wrap(self, value: int) -> "FieldElement":
        return FieldElement(value, self.field)

    # --- arithmetic ----------------------------------------------------------
    def __add__(self, other):
        o = self._value_of(other)
        return NotImplemented if o is None else self._wrap(self.value + o)

    __radd__ = __add__

    def __sub__(self, other):
        o = self._value_of(other)
        return NotImplemented if o is None else self._wrap(self.value - o)

    def __rsub__(self, other):
        o = self._value_of(other)
        return NotImplemented if o is None else self._wrap(o - self.value)

    def __mul__(self, other):
        o = self._value_of(other)
        return NotImplemented if o is None else self._wrap(self.value * o)

    __rmul__ = __mul__

    def __neg__(self):
        return self._wrap(-self.value)

    def inverse(self) -> "FieldElement":
        """The multiplicative inverse. Raise NoInverse for 0 (SDD 8.1)."""
        if self.value == 0:
            raise NoInverse(f"0 has no inverse in Z_{self.field.p}")
        return self._wrap(mod_inverse(self.value, self.field.p))

    def __truediv__(self, other):
        o = self._value_of(other)
        if o is None:
            return NotImplemented
        return self * self._wrap(o).inverse()

    def __rtruediv__(self, other):
        o = self._value_of(other)
        if o is None:
            return NotImplemented
        return self._wrap(o) * self.inverse()

    def __pow__(self, exponent: int):
        if not isinstance(exponent, int) or isinstance(exponent, bool):
            return NotImplemented
        if exponent < 0:
            return self.inverse() ** (-exponent)
        return self._wrap(pow(self.value, exponent, self.field.p))

    # --- comparison / hashing ------------------------------------------------
    def __eq__(self, other):
        o = self._value_of(other)
        return NotImplemented if o is None else self.value == o

    def __hash__(self):
        return hash((self.field.p, self.value))

    # --- conversions -------------------------------------------------------
    def __int__(self):
        return self.value

    def __repr__(self):
        return f"{self.value} (mod {self.field.p})"
