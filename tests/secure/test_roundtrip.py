"""FR8 / SS-2 -- share / reconstruct round trip (SDD 8.4)."""

import pytest

from seclinalg.sharing import ShareSet, reconstruct, share


@pytest.mark.parametrize("n", [1, 2, 3, 5])
def test_reconstruct_of_share_is_identity(field, n):
    for v in range(0, field.p, 9):
        secret = field.element(v)
        assert reconstruct(share(secret, n)) == secret


def test_share_produces_exactly_n_shares(field):
    ss = share(field.element(10), 4)
    assert len(ss) == 4
    assert ss.n == 4


def test_two_sharings_of_the_same_secret_differ(field):
    a = share(field.element(50), 3)
    b = share(field.element(50), 3)
    # astronomically unlikely to be equal; both still reconstruct
    assert a.shares != b.shares
    assert reconstruct(a) == reconstruct(b) == field.element(50)


def test_share_of_plain_int_needs_a_field(field):
    with pytest.raises(ValueError):
        share(7, 3)
    assert reconstruct(share(7, 3, field=field)) == field.element(7)


def test_reconstruct_at_runtime_prime(any_field):
    secret = any_field.element(1234567)
    assert reconstruct(share(secret, 3)) == secret
