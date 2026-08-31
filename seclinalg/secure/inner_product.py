"""Private inner product  [W3]  Must  (story SP-2).

Both operands are shared. Each term x_i * y_i costs one Beaver triple; the k
product shares are summed locally. Reconstruction equals the plaintext dot
product on random inputs (SDD 8.5, VB-1).

Public x shared terms do not need a triple -- use
``seclinalg.sharing.scalar_mul_shares`` for those and add them in locally.
"""

from seclinalg.errors import ShapeError
from seclinalg.sharing import ShareSet, add_shares, share
from seclinalg.secure.beaver import beaver_mul


def private_inner_product(x_shares, y_shares, dealer) -> ShareSet:
    """``x_shares`` and ``y_shares`` are equal-length sequences of ShareSet.
    Returns a ShareSet for sum_i x_i * y_i."""
    x_shares = list(x_shares)
    y_shares = list(y_shares)
    if len(x_shares) != len(y_shares):
        raise ShapeError(f"length mismatch: {len(x_shares)} vs {len(y_shares)}")
    if not x_shares:
        raise ShapeError("inner product of empty vectors")

    n = x_shares[0].n
    field = x_shares[0].field
    acc = share(field.zero, n)                       # sharing of 0 -- neutral
    for xs, ys in zip(x_shares, y_shares):
        term = beaver_mul(xs, ys, dealer.next_triple())
        acc = add_shares(acc, term)
    return acc
