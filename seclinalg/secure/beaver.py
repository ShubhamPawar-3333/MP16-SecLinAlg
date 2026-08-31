"""Shared x shared multiplication with one Beaver triple  [W3]  Must  (SP-4).

    d = open([x] - [a]) ,  e = open([y] - [b])       # d, e are uniform masks
    [xy] = [c] + d*[b] + e*[a] + d*e                 # d*e onto one party's share

Correctness (reconstructed):
    c + d*b + e*a + d*e = ab + (x-a)b + (y-b)a + (x-a)(y-b) = xy
This identity is exactly what the viva asks the team to derive (SDD 8.5, 12.4).
"""


def beaver_mul(x_shares, y_shares, triple):
    """Return a ShareSet for x*y. Consumes `triple`."""
    raise NotImplementedError("SP-1: form d,e locally; open; recombine")
