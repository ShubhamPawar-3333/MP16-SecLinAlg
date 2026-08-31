"""FR4 / LA-1 -- schoolbook multiplication (SDD 8.3)."""

import pytest

from seclinalg.errors import ShapeError
from seclinalg.linalg import multiply
from seclinalg.types import Matrix


def test_hand_computed_2x2(field):
    A = Matrix([[1, 2], [3, 4]], field)
    B = Matrix([[5, 6], [7, 8]], field)
    assert multiply(A, B) == Matrix([[19, 22], [43, 50]], field)


def test_hand_computed_3x3(field):
    A = Matrix([[2, 0, 1], [1, 3, 2], [1, 0, 2]], field)
    B = Matrix([[1, 1, 0], [0, 2, 1], [3, 0, 1]], field)
    assert multiply(A, B) == Matrix([[5, 2, 1], [7, 7, 5], [7, 1, 2]], field)


def test_non_square_shapes(field):
    A = Matrix([[1, 2, 3], [4, 5, 6]], field)          # 2x3
    B = Matrix([[1, 0], [0, 1], [1, 1]], field)        # 3x2
    assert multiply(A, B).shape == (2, 2)


def test_dimension_mismatch_raises_ShapeError(field):
    A = Matrix([[1, 2, 3]], field)                     # 1x3
    B = Matrix([[1, 2]], field)                        # 1x2
    with pytest.raises(ShapeError):
        multiply(A, B)


def test_same_result_at_both_primes(any_field):
    A = Matrix([[10, 20], [30, 40]], any_field)
    B = Matrix([[1, 2], [3, 4]], any_field)
    got = multiply(A, B)
    assert got[0, 0] == any_field.element(70)
    assert got[1, 1] == any_field.element(220)
