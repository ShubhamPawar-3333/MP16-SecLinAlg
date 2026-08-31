"""Private matrix product  [W3]  Should  (story SP-3).

Built from private_inner_product over rows of the left matrix and columns of the
right. An m x k by k x p product consumes m*k*p triples. Reconstruction equals
the plaintext matrix product on random inputs (SDD 8.5, 11).
"""


def private_matrix_product(a_shares, b_shares, dealer):
    """Return a grid of ShareSets for A @ B."""
    raise NotImplementedError("SP-3: inner product per (row, column) pair")
