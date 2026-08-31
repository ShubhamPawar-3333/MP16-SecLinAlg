"""FR6 / LA-3 -- rank, determinant, inverse (SDD 8.3)."""

from seclinalg.linalg import determinant, inverse, rank
from seclinalg.linalg.multiply import multiply
from seclinalg.types import Matrix


def test_rank_full_and_deficient(field):
    full = Matrix([[2, 1, 1], [1, 3, 2], [1, 0, 2]], field)
    deficient = Matrix([[1, 2, 3], [2, 4, 6], [0, 1, 1]], field)   # row2 = 2*row1
    assert rank(full) == 3
    assert rank(deficient) == 2


def test_determinant_matches_hand_computation(field):
    assert determinant(Matrix([[1, 2], [3, 4]], field)) == field.element(-2)
    assert determinant(Matrix([[2, 1, 1], [1, 3, 2], [1, 0, 2]], field)) == field.element(9)


def test_determinant_sign_flips_with_a_row_swap(field):
    assert determinant(Matrix([[0, 1], [1, 0]], field)) == field.element(-1)


def test_determinant_of_singular_is_zero(field):
    assert determinant(Matrix([[1, 2], [2, 4]], field)) == field.zero


def test_inverse_times_original_is_identity(field):
    a = Matrix([[1, 2], [3, 4]], field)
    assert multiply(inverse(a), a) == Matrix.identity(2, field)
    assert multiply(a, inverse(a)) == Matrix.identity(2, field)


def test_inverse_3x3(field):
    a = Matrix([[2, 1, 1], [1, 3, 2], [1, 0, 2]], field)
    assert multiply(a, inverse(a)) == Matrix.identity(3, field)


def test_inverse_at_runtime_prime(any_field):
    a = Matrix([[4, 7], [2, 6]], any_field)
    assert multiply(a, inverse(a)) == Matrix.identity(2, any_field)
