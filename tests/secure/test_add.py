"""FR9 / SS-4 -- local secure addition and public scaling (SDD 8.4)."""

import pytest

from seclinalg.errors import FieldMismatch, ShareCountMismatch
from seclinalg.sharing import (
    add_public,
    add_shares,
    reconstruct,
    scalar_mul_shares,
    share,
)


def test_add_shares_reconstructs_to_the_sum(field):
    for u_val, v_val in [(3, 4), (100, 100), (0, 55), (73, 29)]:
        u = share(field.element(u_val), 3)
        v = share(field.element(v_val), 3)
        assert reconstruct(add_shares(u, v)) == field.element(u_val + v_val)


def test_scalar_mul_shares_reconstructs_to_the_product(field):
    v = share(field.element(21), 3)
    assert reconstruct(scalar_mul_shares(5, v)) == field.element(105)


def test_add_public_shifts_the_secret_by_the_constant(field):
    v = share(field.element(40), 4)
    assert reconstruct(add_public(17, v)) == field.element(57)


def test_add_shares_is_componentwise_and_local(field):
    u = share(field.element(10), 3)
    v = share(field.element(20), 3)
    out = add_shares(u, v)
    for i in range(3):
        assert out[i] == u[i] + v[i]


def test_mismatched_share_sets_raise(field):
    from seclinalg.field import Field

    with pytest.raises(ShareCountMismatch):
        add_shares(share(field.element(1), 3), share(field.element(1), 4))
    with pytest.raises(FieldMismatch):
        add_shares(
            share(field.element(1), 3),
            share(Field(103).element(1), 3),
        )
