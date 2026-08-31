"""The one error hierarchy for the whole library (SDD 10).

Raise the most specific type at the layer that detects the violation, with a
message that names the offending values. Callers catch broadly (SecLinAlgError)
or narrowly (NoUniqueSolution) as they need.
"""


class SecLinAlgError(Exception):
    """Base class for every error the library raises."""


# --- field layer -----------------------------------------------------------
class FieldError(SecLinAlgError):
    """Base for finite-field errors."""


class NotPrime(FieldError):
    """Field(p) constructed with composite or non-positive p."""


class NoInverse(FieldError):
    """inverse() of 0, or of an element not coprime to the modulus."""


class FieldMismatch(FieldError):
    """An operation between values from two different fields."""


# --- type / shape layer --------------------------------------------------------
class ShapeError(SecLinAlgError):
    """Non-rectangular matrix, or a dimension mismatch between operands."""


# --- linear algebra layer ----------------------------------------------------
class SingularError(SecLinAlgError):
    """Base for elimination outcomes that have no unique answer."""


class SingularMatrix(SingularError):
    """inverse() / determinant of a non-invertible matrix."""


class NoUniqueSolution(SingularError):
    """Ax = b is consistent but under-determined (free variables)."""


class InconsistentSystem(SingularError):
    """Ax = b has no solution: a zero row on the left, non-zero on the right."""


# --- secret sharing / secure computation -----------------------------------
class ShareError(SecLinAlgError):
    """Base for secret-sharing errors."""


class ShareCountMismatch(ShareError):
    """Combining share sets that have a different party count n."""


class TripleExhausted(ShareError):
    """A shared x shared multiply was requested with no Beaver triple available."""
