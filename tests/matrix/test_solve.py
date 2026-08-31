"""FR7 / LA-4 -- solve Ax = b, unique case (SDD 8.3)."""

from seclinalg.linalg import solve
from seclinalg.linalg.multiply import multiply
from seclinalg.types import Matrix, Vector


def test_unique_2x2(field):
    a = Matrix([[2, 1], [1, 3]], field)
    x_true = Vector([1, 2], field)
    b = multiply(a, x_true)                 # b = [4, 7]
    assert solve(a, b) == x_true


def test_unique_3x3(field):
    a = Matrix([[2, 1, 1], [1, 3, 2], [1, 0, 2]], field)
    x_true = Vector([3, 1, 4], field)
    b = multiply(a, x_true)
    assert solve(a, b) == x_true


def test_solution_actually_satisfies_the_system(field):
    a = Matrix([[5, 2], [3, 4]], field)
    b = Vector([1, 2], field)
    x = solve(a, b)
    assert multiply(a, x) == b


def test_overdetermined_but_consistent(field):
    # three equations, two unknowns, all agreeing on x = (1, 1)
    a = Matrix([[1, 0], [0, 1], [1, 1]], field)
    b = Vector([1, 1, 2], field)
    assert solve(a, b) == Vector([1, 1], field)


def test_solve_at_runtime_prime(any_field):
    a = Matrix([[7, 3], [2, 5]], any_field)
    x_true = Vector([9, 4], any_field)
    b = multiply(a, x_true)
    assert solve(a, b) == x_true
