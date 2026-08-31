"""Rank, determinant, inverse  [W2]  Must  (stories LA-3, LA-5).

    rank(A)        = number of non-zero pivots
    determinant(A) = product of pivots * (-1)**swaps ; 0 for singular
    inverse(A)     = reduce [A | I] to [I | A^-1] ; raise SingularMatrix
"""

from seclinalg.errors import SingularMatrix


def rank(a) -> int:
    raise NotImplementedError("LA-3: count pivots from row_echelon")


def determinant(a):
    raise NotImplementedError("LA-3: product of pivots * (-1)**swaps")


def inverse(a):
    raise NotImplementedError("LA-3/LA-5: [A|I] -> [I|A^-1]; SingularMatrix")
