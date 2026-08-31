"""Gaussian elimination over a field  [W2]  Must  (story LA-2).

Pivot selection: any non-zero entry in the current column -- the arithmetic is
exact, so there is no stability-based choice. Track row swaps for the
determinant sign (SDD 8.3).
"""

from dataclasses import dataclass


@dataclass
class EchelonResult:
    """Internal return of elimination; feeds rank / det / inverse / solve."""
    matrix: object          # reduced matrix
    pivots: list            # pivot column indices
    swaps: int              # row-swap count, for the determinant sign


def row_echelon(a) -> EchelonResult:
    """Row-reduce a copy of `a` to row-echelon form."""
    raise NotImplementedError("LA-2: normalise pivots with modular inverse")
