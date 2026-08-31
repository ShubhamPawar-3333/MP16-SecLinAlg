"""Field-parameterised Vector and Matrix  [W1]  (stories CT-1, CT-2, CT-3).

No operation mutates its operands; every result is a fresh object (SDD 8.2).
"""

from seclinalg.types.matrix import Matrix
from seclinalg.types.vector import Vector

__all__ = ["Matrix", "Vector"]
