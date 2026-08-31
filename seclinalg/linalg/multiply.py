"""Matrix multiplication  [W1]  Must  (story LA-1).

Schoolbook triple loop, every accumulation a field operation. O(n**3) baseline;
for m x k by k x p: m*k*p multiplications, m*p*(k-1) additions (SDD 8.3, 11).
"""

from seclinalg.errors import ShapeError


def multiply(a, b):
    """Return A @ B over the shared field. Raise ShapeError if a.cols != b.rows."""
    raise NotImplementedError("LA-1: triple loop; docstring the operation count")
