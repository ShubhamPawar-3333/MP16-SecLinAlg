"""Matrix multiplication  [W1]  Must  (story LA-1).

Schoolbook triple loop; every accumulation is a field operation. For an
m x k by k x p product:
    multiplications : m * k * p
    additions       : m * p * (k - 1)
so the cost is O(n**3) for square n (SDD 8.3, 11). Strassen (LA-6) is a separate,
optional module.
"""

from seclinalg.errors import FieldMismatch, ShapeError
from seclinalg.types.matrix import Matrix


def multiply(a: Matrix, b: Matrix) -> Matrix:
    """Return A @ B over the shared field.

    Raises ShapeError when ``a.cols != b.rows``; FieldMismatch when the two
    matrices are over different primes.
    """
    if a.field.p != b.field.p:
        raise FieldMismatch(f"Z_{a.field.p} matrix @ Z_{b.field.p} matrix")
    m, k = a.shape
    k2, p = b.shape
    if k != k2:
        raise ShapeError(f"cannot multiply {a.shape} by {b.shape}")

    field = a.field
    ag, bg = a.to_grid(), b.to_grid()
    result = []
    for i in range(m):
        row = []
        for j in range(p):
            acc = field.zero
            for t in range(k):
                acc = acc + ag[i][t] * bg[t][j]
            row.append(acc)
        result.append(row)
    return Matrix(result, field)
