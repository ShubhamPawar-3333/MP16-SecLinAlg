"""FR6 / FR7 / LA-5 -- exceptional cases are typed errors (SDD 10)."""

import pytest

from seclinalg.errors import (
    InconsistentSystem,
    NoUniqueSolution,
    ShapeError,
    SingularMatrix,
)
from seclinalg.linalg import determinant, inverse, solve
from seclinalg.types import Matrix


def test_inverse_of_singular_raises_SingularMatrix(field):
    with pytest.raises(SingularMatrix):
        inverse(Matrix([[1, 2], [2, 4]], field))


def test_inverse_of_non_square_raises_ShapeError(field):
    with pytest.raises(ShapeError):
        inverse(Matrix([[1, 2, 3], [4, 5, 6]], field))


def test_determinant_of_non_square_raises_ShapeError(field):
    with pytest.raises(ShapeError):
        determinant(Matrix([[1, 2, 3], [4, 5, 6]], field))


def test_underdetermined_solve_raises_NoUniqueSolution(field):
    # x + y = 1 : one equation, two unknowns
    with pytest.raises(NoUniqueSolution):
        solve(Matrix([[1, 1]], field), [1])


def test_inconsistent_solve_raises_InconsistentSystem(field):
    # x + y = 1  and  x + y = 2
    with pytest.raises(InconsistentSystem):
        solve(Matrix([[1, 1], [1, 1]], field), [1, 2])


def test_singular_square_system_is_classified_not_crashed(field):
    a = Matrix([[1, 2], [2, 4]], field)
    with pytest.raises((NoUniqueSolution, InconsistentSystem)):
        solve(a, [3, 6])          # consistent but under-determined
    with pytest.raises((NoUniqueSolution, InconsistentSystem)):
        solve(a, [3, 7])          # inconsistent
