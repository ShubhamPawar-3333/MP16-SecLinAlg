"""Primality checking for Field(p)  [W1]  (story FA-1)."""

from seclinalg.errors import NotPrime


def is_prime(n: int) -> bool:
    """Deterministic trial division. Fine for p = 101 and p = 2**31 - 1."""
    raise NotImplementedError("FA-1: implement trial division up to sqrt(n)")


def require_prime(p: int) -> int:
    """Return p unchanged, or raise NotPrime."""
    raise NotImplementedError("FA-1: call is_prime, raise NotPrime otherwise")
