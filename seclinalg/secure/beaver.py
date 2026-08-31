"""Shared x shared multiplication with one Beaver triple  [W3]  Must  (SP-1, SP-4).

Given [x], [y] and a triple ([a], [b], [c]) with c = a*b:

    [d] = [x] - [a]        [e] = [y] - [b]          (local)
    d = open([d])          e = open([e])            (the only values revealed)
    [xy] = [c] + d*[b] + e*[a] + d*e                (local; d*e onto one share)

Why opening d, e is safe: a and b are uniform and secret, so d and e are uniform
masks independent of x and y -- two random numbers (SDD 12.4).

Correctness, reconstructed:
    c + d*b + e*a + d*e
  = ab + (x-a)b + (y-b)a + (x-a)(y-b)
  = xy
This identity is exactly what the viva asks the team to derive (SDD 8.5).
"""

from seclinalg.sharing import (
    ShareSet,
    add_public,
    add_shares,
    reconstruct,
    scalar_mul_shares,
    sub_shares,
)


def beaver_mul(x_shares: ShareSet, y_shares: ShareSet, triple) -> ShareSet:
    """Return a fresh ShareSet for x*y. Consumes ``triple``."""
    a, b, c = triple.a, triple.b, triple.c

    d = reconstruct(sub_shares(x_shares, a))      # open the mask x - a
    e = reconstruct(sub_shares(y_shares, b))      # open the mask y - b

    out = add_shares(c, scalar_mul_shares(d, b))
    out = add_shares(out, scalar_mul_shares(e, a))
    out = add_public(d * e, out)
    return out
