"""Rank, determinant, inverse  [W2]  Must  (stories LA-3, LA-5).

Each of these is a one-line read of the reduced row-echelon form (SDD 8.3):

    rank(A)        = number of pivots
    determinant(A) = (product of the raw pivots) * (-1) ** swaps   [square only]
                     -- 0 when the matrix is rank-deficient
    inverse(A)     = reduce [A | I]; if the left block became I, the right block
                     is A**-1, else the matrix is singular
"""

from seclinalg.errors import ShapeError, SingularMatrix
from seclinalg.linalg.elimination import row_echelon
from seclinalg.types.matrix import Matrix


def rank(a: Matrix) -> int:
    return row_echelon(a).rank


def determinant(a: Matrix):
    rows, cols = a.shape
    if rows != cols:
        raise ShapeError(f"determinant is defined only for a square matrix, got {a.shape}")

    result = row_echelon(a)
    if result.rank < rows:
        return a.field.zero                     # singular

    acc = a.field.one
    for pivot_value in result.pivot_values:
        acc = acc * pivot_value
    return -acc if result.swaps % 2 else acc


def inverse(a: Matrix) -> Matrix:
    rows, cols = a.shape
    if rows != cols:
        raise ShapeError(f"only a square matrix has an inverse, got {a.shape}")

    n = rows
    augmented = a.hstack(Matrix.identity(n, a.field))
    result = row_echelon(augmented)

    # invertible  <=>  the left block reduced exactly to the identity
    if result.pivots != list(range(n)):
        raise SingularMatrix(f"matrix is not invertible (rank {result.rank} < {n})")

    grid = result.matrix.to_grid()
    right_block = [row[n:] for row in grid]
    return Matrix(right_block, a.field)
