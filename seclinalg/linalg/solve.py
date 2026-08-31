"""Solve Ax = b  [W2]  Must  (stories LA-4, LA-5).

Reduce the augmented matrix [A | b] and classify the outcome (SDD 8.3):

    unique          -> return x as a Vector
    NoUniqueSolution   -> consistent but under-determined (a free variable)
    InconsistentSystem -> some row reads  0 ... 0 | nonzero
"""

from seclinalg.errors import InconsistentSystem, NoUniqueSolution, ShapeError
from seclinalg.linalg.elimination import row_echelon
from seclinalg.types.matrix import Matrix
from seclinalg.types.vector import Vector


def _as_column(b, field, expected_len: int) -> list:
    """Coerce b (Vector, Matrix n x 1, or a plain sequence) to a list of
    exactly ``expected_len`` FieldElements."""
    if isinstance(b, Vector):
        entries = list(b)
    elif isinstance(b, Matrix):
        if b.shape[1] != 1:
            raise ShapeError(f"right-hand side must be a column, got {b.shape}")
        entries = [b[i, 0] for i in range(b.shape[0])]
    else:
        entries = [field.element(x) for x in b]

    if len(entries) != expected_len:
        raise ShapeError(f"right-hand side has length {len(entries)}, expected {expected_len}")
    return [field.element(x) for x in entries]


def solve(a: Matrix, b) -> Vector:
    """Return x with A @ x == b over the field, or raise."""
    field = a.field
    zero = field.zero
    m, n = a.shape
    rhs = _as_column(b, field, m)

    augmented = a.hstack(Matrix([[x] for x in rhs], field))
    result = row_echelon(augmented)
    grid = result.matrix.to_grid()

    # inconsistent: a row that is all zero across A but non-zero in the b column
    for row in grid:
        if all(x == zero for x in row[:n]) and row[n] != zero:
            raise InconsistentSystem("system has no solution")

    # under-determined: fewer pivots inside the A block than unknowns
    a_pivots = [c for c in result.pivots if c < n]
    if len(a_pivots) < n:
        free = n - len(a_pivots)
        raise NoUniqueSolution(f"system is under-determined ({free} free variable(s))")

    # unique: pivot i sits at row i, RREF has 1 on the diagonal of the pivot rows
    x = [zero] * n
    for pivot_row, col in enumerate(a_pivots):
        x[col] = grid[pivot_row][n]
    return Vector(x, field)
