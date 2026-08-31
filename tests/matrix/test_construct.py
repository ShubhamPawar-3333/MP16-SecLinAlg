"""FR2 / CT-1 -- construction, shape, indexing (SDD 8.2)."""

import pytest

from seclinalg.errors import ShapeError
from seclinalg.types import Matrix, Vector


def test_ragged_row_list_raises_ShapeError(field):
    with pytest.raises(ShapeError):
        Matrix([[1, 2, 3], [4, 5]], field)


def test_empty_matrix_raises_ShapeError(field):
    with pytest.raises(ShapeError):
        Matrix([], field)
    with pytest.raises(ShapeError):
        Matrix([[], []], field)


def test_shape_property(field):
    m = Matrix([[1, 2, 3], [4, 5, 6]], field)
    assert m.shape == (2, 3)


def test_entries_are_reduced_into_the_field(field):
    m = Matrix([[field.p, -1], [2 * field.p + 3, 100]], field)
    assert m[0, 0] == field.zero
    assert m[0, 1] == field.element(field.p - 1)
    assert m[1, 0] == field.element(3)


def test_setitem_mutates_in_place_only(field):
    m = Matrix([[1, 2], [3, 4]], field)
    m[0, 1] = 99
    assert m[0, 1] == field.element(99)
    with pytest.raises(TypeError):
        m[0] = [1, 1]


def test_getitem_row_is_a_copy(field):
    m = Matrix([[1, 2], [3, 4]], field)
    row = m[0]
    row[0] = field.element(0)
    assert m[0, 0] == field.element(1)


def test_identity_and_zeros(field):
    ident = Matrix.identity(3, field)
    assert ident[0, 0] == field.one and ident[0, 1] == field.zero
    assert Matrix.zeros(2, 3, field).shape == (2, 3)


def test_vector_construction_and_length(field):
    v = Vector([1, 2, 3], field)
    assert len(v) == 3 and v[2] == field.element(3)
    with pytest.raises(ShapeError):
        Vector([], field)
