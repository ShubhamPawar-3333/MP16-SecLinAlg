"""Matrix algorithms  [W1 multiply / W2 the rest]  (stories LA-1..LA-6).

Everything here is exact over the field. Pivot normalisation multiplies by a
modular inverse -- never a floating-point division (SDD 8.3, 12.2).
"""

from seclinalg.linalg.analysis import determinant, inverse, rank
from seclinalg.linalg.elimination import EchelonResult, row_echelon
from seclinalg.linalg.multiply import multiply
from seclinalg.linalg.solve import solve

__all__ = [
    "multiply", "row_echelon", "EchelonResult",
    "rank", "determinant", "inverse", "solve",
]
