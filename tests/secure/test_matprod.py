"""FR10 / SP-3 / VB-1 -- private matrix product vs. plaintext (SDD 8.5)."""

import random

from seclinalg.linalg.multiply import multiply
from seclinalg.sharing import reconstruct, share
from seclinalg.secure import Dealer
from seclinalg.secure.mat_product import private_matrix_product
from seclinalg.types import Matrix


def _share_grid(mat: Matrix, n: int):
    return [[share(mat[i, j], n) for j in range(mat.shape[1])] for i in range(mat.shape[0])]


def _reconstruct_grid(grid, field) -> Matrix:
    return Matrix([[int(reconstruct(cell)) for cell in row] for row in grid], field)


def test_matrix_product_matches_plaintext_fixed(field):
    a = Matrix([[1, 2, 3], [4, 5, 6]], field)
    b = Matrix([[7, 8], [9, 10], [11, 12]], field)
    dealer = Dealer(field, n=3)

    out = private_matrix_product(_share_grid(a, 3), _share_grid(b, 3), dealer)
    assert _reconstruct_grid(out, field) == multiply(a, b)
    assert dealer.issued == 2 * 3 * 2          # m * k * p triples


def test_matrix_product_matches_plaintext_randomised(field):
    rng = random.Random(31415)
    for _ in range(5):
        m, k, p = rng.randint(1, 3), rng.randint(1, 3), rng.randint(1, 3)
        a = Matrix([[rng.randrange(field.p) for _ in range(k)] for _ in range(m)], field)
        b = Matrix([[rng.randrange(field.p) for _ in range(p)] for _ in range(k)], field)
        dealer = Dealer(field, n=3)
        out = private_matrix_product(_share_grid(a, 3), _share_grid(b, 3), dealer)
        assert _reconstruct_grid(out, field) == multiply(a, b)


def test_matrix_product_at_runtime_prime(any_field):
    a = Matrix([[2, 3], [5, 7]], any_field)
    b = Matrix([[1, 4], [6, 8]], any_field)
    dealer = Dealer(any_field, n=3)
    out = private_matrix_product(_share_grid(a, 3), _share_grid(b, 3), dealer)
    assert _reconstruct_grid(out, any_field) == multiply(a, b)
