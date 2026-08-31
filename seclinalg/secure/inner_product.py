"""Private inner product  [W3]  Must  (story SP-2).

Public x shared terms: local via scalar_mul_shares.
Shared x shared terms: one Beaver triple each.
Sum the k product shares locally; reconstruct equals the plaintext dot product
on random inputs (SDD 8.5, VB-1).
"""


def private_inner_product(x_shares, y_shares, dealer):
    """Return a ShareSet for sum_i x_i * y_i."""
    raise NotImplementedError("SP-2: one triple per shared x shared term; local sum")
