"""Solve Ax = b  [W2]  Must  (stories LA-4, LA-5).

Reduce [A | b]. Return the unique solution when one exists, else raise:
    NoUniqueSolution   -- consistent but under-determined
    InconsistentSystem -- zero row on the left, non-zero on the right
(SDD 8.3)
"""

from seclinalg.errors import InconsistentSystem, NoUniqueSolution


def solve(a, b):
    """Return x with A @ x == b over the field."""
    raise NotImplementedError("LA-4: reduce augmented matrix; classify outcome")
