"""FR5 / LA-2 -- Gaussian elimination, no floating point (SDD 8.3)."""

from seclinalg.linalg.elimination import row_echelon
from seclinalg.types import Matrix


def test_reduced_form_has_unit_pivots(field):
    a = Matrix([[2, 4, 2], [4, 9, 7], [2, 5, 9]], field)
    res = row_echelon(a)
    for r, c in enumerate(res.pivots):
        assert res.matrix[r, c] == field.one


def test_row_swap_is_counted(field):
    a = Matrix([[0, 1], [1, 0]], field)
    res = row_echelon(a)
    assert res.swaps == 1
    assert res.matrix == Matrix.identity(2, field)


def test_no_swap_when_pivot_already_present(field):
    a = Matrix([[1, 2], [3, 4]], field)
    assert row_echelon(a).swaps == 0


def test_zero_pivot_column_becomes_a_free_column(field):
    # second row is 2x the first -> rank 1, one pivot in column 0
    a = Matrix([[1, 2, 3], [2, 4, 6]], field)
    res = row_echelon(a)
    assert res.pivots == [0]
    assert res.rank == 1
    assert all(x == field.zero for x in res.matrix[1])


def test_full_rank_reduces_to_identity(field):
    a = Matrix([[2, 1, 1], [1, 3, 2], [1, 0, 2]], field)
    res = row_echelon(a)
    assert res.matrix == Matrix.identity(3, field)
    assert res.pivots == [0, 1, 2]


def test_original_matrix_is_not_mutated(field):
    a = Matrix([[0, 5], [2, 3]], field)
    before = a.to_grid()
    row_echelon(a)
    assert a.to_grid() == before
