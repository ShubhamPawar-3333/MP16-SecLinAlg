"""Primality checking for Field(p)  [W1]  (story FA-1).

Deterministic trial division. The runtime prime is 2**31 - 1, whose square root
is about 46341, so the loop below runs in well under a millisecond -- fast
enough that the mini-project never needs a probabilistic test.
"""

from seclinalg.errors import NotPrime


def is_prime(n: int) -> bool:
    """True iff n is a prime. Trial division by 2 and then odd factors up to
    sqrt(n): if n has any factor it has one no larger than its square root."""
    if n < 2:
        return False
    if n < 4:            # 2 and 3
        return True
    if n % 2 == 0:
        return False
    factor = 3
    while factor * factor <= n:
        if n % factor == 0:
            return False
        factor += 2
    return True


def require_prime(p: int) -> int:
    """Return p unchanged when it is a positive prime int, else raise NotPrime.

    A bool is rejected explicitly: True would otherwise slip through as the
    integer 1 in some call paths.
    """
    if isinstance(p, bool) or not isinstance(p, int):
        raise NotPrime(f"modulus must be an int, got {p!r}")
    if not is_prime(p):
        raise NotPrime(f"{p} is not prime")
    return p
