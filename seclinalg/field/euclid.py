"""Extended Euclidean algorithm  [W1]  (story FA-2).

The modular inverse is the one place students are tempted to write a search
(`for x in range(p): if a*x % p == 1`). That is O(p) and hopeless at the runtime
prime. Extended Euclid is O(log p) -- this contrast is a viva talking point
(SDD 11).
"""

from seclinalg.errors import NoInverse


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, s, t) with  s*a + t*b == g == gcd(a, b).

    Iterative form: carry two coefficient pairs alongside the remainder pair and
    apply the same quotient step to all three.
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t


def mod_inverse(a: int, p: int) -> int:
    """Return a**-1 mod p in [0, p). Raise NoInverse when gcd(a, p) != 1
    (that is, when a is 0 mod p, or -- for a non-prime modulus -- shares a
    factor with p)."""
    a %= p
    g, s, _ = extended_gcd(a, p)
    if g != 1:
        raise NoInverse(f"{a} has no inverse mod {p} (gcd = {g})")
    return s % p
