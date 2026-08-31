"""FR1 / FA-3 -- field laws over p = 101 (SDD 8.1).

`field` comes from tests/conftest.py and is Field(101). Small enough to sweep
every element where that is cheap.
"""

import itertools

import pytest

from seclinalg.errors import NotPrime
from seclinalg.field import Field


def test_field_rejects_composite_modulus():
    with pytest.raises(NotPrime):
        Field(100)


def test_field_rejects_non_positive_modulus():
    with pytest.raises(NotPrime):
        Field(1)
    with pytest.raises(NotPrime):
        Field(-7)


def test_reduction_of_negative_and_large_integers(field):
    p = field.p
    assert field.element(-1) == field.element(p - 1)
    assert field.element(p) == field.zero
    assert field.element(3 * p + 4) == field.element(4)
    assert field.element(-(p + 2)) == field.element(p - 2)


def test_additive_and_multiplicative_identity(field):
    for a in range(field.p):
        x = field.element(a)
        assert x + field.zero == x
        assert x * field.one == x


def test_additive_inverse(field):
    for a in range(field.p):
        x = field.element(a)
        assert x + (-x) == field.zero


def test_commutativity(field):
    for a in range(0, field.p, 7):
        for b in range(0, field.p, 5):
            x, y = field.element(a), field.element(b)
            assert x + y == y + x
            assert x * y == y * x


def test_associativity(field):
    sample = [field.element(v) for v in (0, 1, 2, 37, 99, 100)]
    for x, y, z in itertools.product(sample, repeat=3):
        assert (x + y) + z == x + (y + z)
        assert (x * y) * z == x * (y * z)


def test_distributivity(field):
    sample = [field.element(v) for v in (0, 1, 3, 47, 100)]
    for x, y, z in itertools.product(sample, repeat=3):
        assert x * (y + z) == x * y + x * z


def test_operations_across_two_fields_raise(field):
    from seclinalg.errors import FieldMismatch

    other = Field(103)
    with pytest.raises(FieldMismatch):
        field.element(2) + other.element(2)


def test_same_prime_different_instances_interoperate():
    a = Field(101).element(40)
    b = Field(101).element(70)
    assert (a + b) == Field(101).element(9)
