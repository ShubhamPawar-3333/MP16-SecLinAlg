"""Extended Euclidean algorithm  [W1]  (story FA-2).

Complexity: O(log p) division steps -- never a search over all residues.
This is a viva talking point (SDD 11).
"""


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, s, t) with s*a + t*b == g == gcd(a, b)."""
    raise NotImplementedError("FA-2: iterative extended Euclid")


def mod_inverse(a: int, p: int) -> int:
    """Return a^{-1} mod p. Raise NoInverse when gcd(a, p) != 1."""
    raise NotImplementedError("FA-2: use extended_gcd; check g == 1")
