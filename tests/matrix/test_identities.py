"""FR3 / CT-3 -- algebraic identities over p = 101 (SDD 8.2)."""

from seclinalg.types import Matrix, Vector


def _A(field):
    return Matrix([[1, 2, 3], [4, 5, 6]], field)


def _B(field):
    return Matrix([[7, 8], [9, 10], [11, 12]], field)


def test_A_plus_zero_equals_A(field):
    A = _A(field)
    assert A.add(Matrix.zeros(*A.shape, field)) == A


def test_A_minus_A_is_zero(field):
    A = _A(field)
    assert A.sub(A) == Matrix.zeros(*A.shape, field)


def test_A_times_identity_equals_A(field):
    A = _A(field)
    assert A @ Matrix.identity(3, field) == A
    assert Matrix.identity(2, field) @ A == A


def test_double_transpose_is_identity(field):
    A = _A(field)
    assert A.transpose().transpose() == A


def test_transpose_of_product(field):
    A, B = _A(field), _B(field)
    assert (A @ B).transpose() == B.transpose() @ A.transpose()


def test_scalar_mul_distributes_over_addition(field):
    A = _A(field)
    k = field.element(7)
    assert A.scalar_mul(k).add(A.scalar_mul(k)) == A.add(A).scalar_mul(k)


def test_hand_computed_2x2(field):
    A = Matrix([[1, 2], [3, 4]], field)
    B = Matrix([[5, 6], [7, 8]], field)
    assert A @ B == Matrix([[19, 22], [43, 50]], field)


def test_vector_dot_matches_row_by_column(field):
    u = Vector([1, 2, 3], field)
    v = Vector([4, 5, 6], field)
    assert u.dot(v) == field.element(32)
