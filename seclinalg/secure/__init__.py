"""Secure computation over shared values  [W3]  (stories SP-1..SP-4, VB-1).

Local and free: addition, public scaling. Needs a Beaver triple: shared x shared
multiplication. Out of scope, would need a real protocol: triple generation,
malicious security, networking (SDD 8.5, 12.1).
"""

from seclinalg.secure.beaver import beaver_mul
from seclinalg.secure.dealer import BeaverTriple, Dealer
from seclinalg.secure.inner_product import private_inner_product
from seclinalg.secure.mat_product import private_matrix_product

__all__ = [
    "Dealer", "BeaverTriple", "beaver_mul",
    "private_inner_product", "private_matrix_product",
]
