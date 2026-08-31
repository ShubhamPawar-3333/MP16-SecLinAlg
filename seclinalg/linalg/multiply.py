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
from seclinalg.types.vector import Vector


def multiply(a: Matrix, b):
    """Return A @ B over the shared field.

    ``b`` is a Matrix, or a Vector treated as a single column (the result is
    then a Vector). Raises ShapeError when the inner dimensions disagree;
    FieldMismatch when the operands are over different primes.
    """
    if isinstance(b, Vector):
        column = Matrix([[x] for x in b], a.field)
        product = multiply(a, column)
        return Vector([product[i, 0] for i in range(product.shape[0])], a.field)

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
