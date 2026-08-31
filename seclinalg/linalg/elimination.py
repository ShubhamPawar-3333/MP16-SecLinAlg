"""Gaussian elimination over a field  [W2]  Must  (story LA-2).

Produces the *reduced* row-echelon form (Gauss-Jordan): every pivot is 1 and is
the only non-zero entry in its column. rank / determinant / inverse / solve all
read their answer straight off this one result.

Key points for the viva (SDD 8.3, 12.2):
  * Pivot selection takes *any* non-zero entry in the current column. There is no
    partial-pivoting-for-stability choice because the arithmetic is exact.
  * Pivot normalisation multiplies the row by ``pivot.inverse()`` -- never a
    floating-point division.
  * Row swaps are counted so the determinant keeps the right sign.
  * The raw pivot values (before normalisation) are kept so ``determinant`` can
    multiply them back together.
"""

from dataclasses import dataclass, field as _dc_field

from seclinalg.types.matrix import Matrix


@dataclass
class EchelonResult:
    """The output of :func:`row_echelon`.

    matrix        -- the reduced row-echelon form, as a Matrix
    pivots        -- pivot column indices, in increasing order (one per pivot row)
    swaps         -- number of row swaps performed
    pivot_values  -- the raw pivot entry divided out at each step (FieldElement),
                     in the same order as ``pivots``
    """

    matrix: Matrix
    pivots: list = _dc_field(default_factory=list)
    swaps: int = 0
    pivot_values: list = _dc_field(default_factory=list)

    @property
    def rank(self) -> int:
        return len(self.pivots)


def row_echelon(a: Matrix) -> EchelonResult:
    """Row-reduce a copy of ``a`` to reduced row-echelon form."""
    field = a.field
    zero = field.zero
    g = a.to_grid()                     # list[list[FieldElement]], a private copy
    n_rows = len(g)
    n_cols = len(g[0])

    swaps = 0
    pivots: list[int] = []
    pivot_values: list = []
    pivot_row = 0

    for col in range(n_cols):
        # find a row at or below pivot_row with a non-zero entry in this column
        found = None
        for i in range(pivot_row, n_rows):
            if g[i][col] != zero:
                found = i
                break
        if found is None:
            continue                    # free column, move on

        if found != pivot_row:
            g[pivot_row], g[found] = g[found], g[pivot_row]
            swaps += 1

        raw_pivot = g[pivot_row][col]
        pivots.append(col)
        pivot_values.append(raw_pivot)

        # normalise the pivot row so the pivot becomes 1
        inv = raw_pivot.inverse()
        g[pivot_row] = [x * inv for x in g[pivot_row]]

        # clear this column everywhere else
        for i in range(n_rows):
            if i != pivot_row and g[i][col] != zero:
                factor = g[i][col]
                g[i] = [xi - factor * xr for xi, xr in zip(g[i], g[pivot_row])]

        pivot_row += 1
        if pivot_row == n_rows:
            break

    return EchelonResult(Matrix(g, field), pivots, swaps, pivot_values)
