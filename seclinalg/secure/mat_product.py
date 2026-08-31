"""Private matrix product  [W3]  Should  (story SP-3).

Built from the private inner product over the rows of the left matrix and the
columns of the right. An m x k by k x p product consumes m*k*p triples.
Reconstruction equals the plaintext matrix product on random inputs
(SDD 8.5, 11).

Inputs and output are grids (list of rows) of ShareSet, so this module stays
independent of the Matrix type.
"""

from seclinalg.errors import ShapeError
from seclinalg.secure.inner_product import private_inner_product


def private_matrix_product(a_grid, b_grid, dealer) -> list:
    """``a_grid`` is m rows of k ShareSet; ``b_grid`` is k rows of p ShareSet.
    Returns m rows of p ShareSet."""
    a_grid = [list(row) for row in a_grid]
    b_grid = [list(row) for row in b_grid]

    m = len(a_grid)
    k = len(a_grid[0])
    if len(b_grid) != k:
        raise ShapeError(f"cannot multiply {m}x{k} by {len(b_grid)}x{len(b_grid[0])}")
    p = len(b_grid[0])

    b_cols = [[b_grid[t][j] for t in range(k)] for j in range(p)]

    result = []
    for i in range(m):
        row = [private_inner_product(a_grid[i], b_cols[j], dealer) for j in range(p)]
        result.append(row)
    return result
