"""FR1 / FA-2 / FA-3 -- modular inverse via extended Euclid (SDD 8.1, 11)."""

import pytest

from seclinalg.errors import NoInverse
from seclinalg.field.euclid import extended_gcd, mod_inverse


@pytest.mark.parametrize("a, b", [(240, 46), (101, 13), (17, 0), (0, 5), (2**31 - 1, 7)])
def test_extended_gcd_bezout_identity(a, b):
    g, s, t = extended_gcd(a, b)
    assert s * a + t * b == g


def test_every_nonzero_element_has_an_inverse(field):
    for a in range(1, field.p):
        x = field.element(a)
        assert x * x.inverse() == field.one


def test_inverse_is_involutive(field):
    for a in range(1, field.p):
        x = field.element(a)
        assert x.inverse().inverse() == x


def test_inverse_of_zero_raises(field):
    with pytest.raises(NoInverse):
        field.zero.inverse()


def test_mod_inverse_rejects_zero_and_non_coprime():
    with pytest.raises(NoInverse):
        mod_inverse(0, 101)
    with pytest.raises(NoInverse):
        mod_inverse(4, 8)          # non-prime modulus, shared factor 2


def test_division_equals_multiply_by_inverse(field):
    a, b = field.element(7), field.element(19)
    assert a / b == a * b.inverse()
    assert (a / b) * b == a


def test_inverse_runtime_prime():
    from seclinalg.field import Field

    p = 2**31 - 1
    f = Field(p)
    x = f.element(123456789)
    assert x * x.inverse() == f.one


def test_pow_uses_inverse_for_negative_exponent(field):
    x = field.element(5)
    assert x ** -1 == x.inverse()
    assert x ** -3 == x.inverse() ** 3
